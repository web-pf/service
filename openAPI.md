# OpenAPI for WebPF service

All the api url shall be prefixed with '/api/[VERSION]', like `/api/v1/user/1`

> api version: v1

## authentification and user portal

#### get current user information

```ts
interface request {
  url: '/user/current'
  method: 'get'
}
interface response {}
```

#### create a new user

```ts
interface request {
  url: '/user/new'
  method: 'put'
}
interface response {
  id: number
}
```

#### login

```ts
interface request {
  url: '/user'
  method: 'post'
  data: {
    
  }
}
```
