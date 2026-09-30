import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    documentation_and_ui: {
      executor: 'constant-vus',
      vus: 5,
      duration: '15s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1500'],
  },
};

const endpoints = [
  'http://airflow-webserver:8080/health',
  'http://dbt-docs:8081/',
  'http://grafana:3000/api/health',
  'http://prometheus:9090/-/ready',
];

export default function () {
  for (const url of endpoints) {
    const response = http.get(url);
    check(response, { [`${url} responde 2xx`]: (item) => item.status >= 200 && item.status < 300 });
  }
  sleep(1);
}
