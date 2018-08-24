## ROADMAP

This roadmap is organized into stages of development, leading towards a backend for (mostly) real-time collaboration.

### Stage I

- PPMagics
  - [x] Hive magic
  - [x] Teradata Magic
  - [x] STS (Spark Thrift Server) magic
  - [x] Presto magic
  - [x] CSV magic
  - [x] Run Magic

- [x] Tableau publish

### Stage II

- [x] Save notebooks back to S3
- [x] Delete notebooks

### Stage III

- [x] Render page using nteract/nteract components
- [ ] Configurable base path for commuter app
- [ ] Start outlining an authentication and permissions strategy

### Stage IV

- [ ] Create server side in-memory model of notebook and transient models, push to clients
- [ ] Provide/use kernels from configured source (e.g. tmpnb.org, jupyterhub, or your private setup)