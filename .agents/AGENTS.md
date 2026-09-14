# Workspace Agent Guidelines

## 1. Single Living Source of Truth: `PROJECT_INFO.md`
- The file [`PROJECT_INFO.md`](file:///d:/SOFTWARES/xampp82new/htdocs/androidapps/arti/PROJECT_INFO.md) at the workspace root is the living project encyclopedia.
- **MANDATORY**: Before making architectural changes, modifying data schemas, updating endpoints, or altering state handling, you **MUST read and refer to `PROJECT_INFO.md`**.
- **MANDATORY**: Whenever you make changes that alter:
  - Dataset counts or categories
  - API endpoints or payload shapes
  - Database schema or seeder logic in `toolsite`
  - Front-end controllers, PixiJS animation engine, or reader settings
  You **MUST update `PROJECT_INFO.md`** as part of your turn before completing the task.

## 2. Core Architectural Rules
- **Pure API Data Source**: All runtime data originates from the Laravel REST API (`http://localhost:8000/api/arti`). Never import or bundle static/mock JSON datasets as working data.
- **No Dummy Aartis**: Only authentic devotional hymns are allowed in the database and frontend. Never add dummy/placeholder records.
- **Offline Persistence**: API data is cached locally via `StorageService` for instantaneous 0ms startup and offline use.
- **Local Images Only**: Devotional artwork must be stored locally in `public/assets/images/arties/` and `toolsite/public/images/arties/`. Never depend on external image CDNs.
