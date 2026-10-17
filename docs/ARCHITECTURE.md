# Architecture

```text
Browser dashboard (HTML/CSS/JavaScript)
              |
              | HTTP / JSON
              v
       FastAPI application
       |       |       |
       |       |       +--> /api/simulate (read-only what-if)
       |       +----------> /api/recommendations
       +------------------> /api/inventory and /api/summary
              |
              v
        SQLite inventory

Deployment target: LinuxONE Community Cloud Linux virtual server
CI: GitHub Actions runs automated unit/API tests on pushes and pull requests
```

This diagram describes the intended deployment architecture. LinuxONE deployment is not complete until a live instance is created and the application is verified on that host.
