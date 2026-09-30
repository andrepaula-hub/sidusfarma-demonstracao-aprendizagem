# Publicação privada do Artefato 3 no Cloudflare

O pacote publicado é produzido por allowlist e contém somente o relatório
quantitativo, sete gráficos agregados e os assets necessários. Dados brutos,
documentos de contexto, documentos internos e contratos JSON com mapas por ID
permanecem fora do Cloudflare Pages.

## Autenticação

A proteção usa o **Cloudflare Access** na frente do domínio `*.pages.dev`.
Cada visitante se autentica por identidade individual, preferencialmente com
One-time PIN por e-mail ou com o provedor de identidade da organização. Não
existe senha compartilhada no repositório, em JavaScript ou no HTML.

O deploy usa **Direct Upload** via Wrangler e só aparece em `develop` quando
`CLOUDFLARE_ACCESS_CONFIRMED=true` estiver configurada. Essa variável deve ser
criada somente depois de proteger o domínio de produção e os previews no
Cloudflare Access. Ela é um gate operacional, não uma prova automática da
configuração.

## Ordem segura do primeiro deploy

1. Criar um projeto Cloudflare Pages de **Direct Upload**, sem enviar conteúdo,
   com `develop` como branch de produção.
2. Em **Workers & Pages > projeto > Settings**, habilitar a política do Access.
3. Conferir duas aplicações no Access: o domínio exato `projeto.pages.dev` e os
   previews `*.projeto.pages.dev`. Se a primeira aplicação tiver wildcard,
   removê-lo do hostname e reativar a proteção dos previews.
4. Criar uma política `Allow` somente para os e-mails ou domínios autorizados.
   O Access é deny-by-default para quem não corresponde à regra.
5. Criar um API Token com permissão **Account > Cloudflare Pages > Edit**.
6. Cadastrar no GitLab, como variáveis protegidas e mascaradas quando aplicável:

   - `CLOUDFLARE_ACCOUNT_ID`;
   - `CLOUDFLARE_API_TOKEN`;
   - `CLOUDFLARE_PAGES_PROJECT`;
   - `CLOUDFLARE_ACCESS_CONFIRMED=true`.

7. Integrar a branch em `develop` e executar manualmente o job
   `deploy-private-cloudflare-pages`.
8. Em sessão anônima, validar que a raiz e uma URL direta de imagem exigem
   autenticação. Depois, validar um usuário autorizado e um não autorizado.

O token nunca deve ser salvo em `.env`, commits, logs, screenshots ou mensagens.

## Validação local

```powershell
python -m scripts.publication.prepare_private_site
python -m mkdocs build --strict --config-file mkdocs.private.yml --site-dir public
python -m scripts.publication.privacy_gate --site-dir public
```

O diretório `.build/private-docs` e o resultado `public/` são temporários e
permanecem no `.gitignore`.

## Referências operacionais

- [Cloudflare Pages Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)
- [Direct Upload com CI](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)
- [Proteção do domínio pages.dev com Access](https://developers.cloudflare.com/pages/platform/known-issues/#enable-access-on-your-pagesdev-domain)
