# Demo-Ready Knowledge Graph Application

## Goal

Create a polished, feature-complete demo that can be set up and running in minimal steps while maintaining professional quality.

## Current State Analysis

- ✅ Backend API with full CRUD endpoints
- ✅ 3D graph visualization working
- ✅ Database setup with SQLite (no external DB needed)
- ✅ Basic create functionality
- ❌ Missing: Edit/Delete UI, backend search integration, auto-refresh, easy setup

## Implementation Plan

### Phase 1: Simplify Setup & Auto-Configuration

**Goal**: Make the demo work with just 2 commands (install + run)

1. **Auto-seed database on startup**

   - Modify `backend/main.py` startup event to check if database is empty
   - If empty, automatically seed with sample data from mock repository
   - File: `backend/main.py` (startup event)

2. **Create startup scripts**

   - Add `start-backend.sh` and `start-backend.bat` for Windows
   - Add `start-frontend.sh` and `start-frontend.bat` for Windows
   - Scripts handle venv activation, dependency checks, and server startup
   - Files: Root directory scripts

3. **Update README with quick start**

   - Add "Quick Start" section with 2-command setup
   - Document auto-seeding behavior
   - File: `project1/README.md`

### Phase 2: Add Missing Critical Features

**Goal**: Complete the CRUD functionality and improve UX

4. **Add Edit/Delete UI for Companies**

   - Add edit button on company detail page (`/company/[nodeId]/page.tsx`)
   - Create edit form modal/page for companies
   - Add delete confirmation dialog
   - Add API functions: `updateCompany`, `deleteCompany` in `frontend/lib/api.ts`
   - Files: `frontend/app/company/[nodeId]/page.tsx`, `frontend/lib/api.ts`

5. **Add Edit/Delete UI for Relationships**

   - Add relationship management section on company detail page
   - Show connected relationships with edit/delete actions
   - Create relationship edit form
   - Add API functions: `updateRelationship`, `deleteRelationship` in `frontend/lib/api.ts`
   - Files: `frontend/app/company/[nodeId]/page.tsx`, `frontend/lib/api.ts`

6. **Integrate Backend Search API**

   - Replace client-side search with backend `/api/search` endpoint
   - Add debounced search input
   - Show loading states during search
   - Files: `frontend/app/page.tsx`, `frontend/lib/api.ts`

7. **Auto-refresh Graph After Mutations**

   - Add refresh callback to `useGraphData` hook
   - Call refresh after create/update/delete operations
   - Show loading state during refresh
   - Files: `frontend/hooks/useGraphData.ts`, mutation components

### Phase 3: Polish & Error Handling

**Goal**: Make it feel production-ready

8. **Improve Error Handling**

   - Add user-friendly error messages
   - Handle network errors gracefully
   - Show toast notifications for success/error
   - Files: All API call sites, create error boundary component

9. **Add Loading States**

   - Loading indicators for all async operations
   - Skeleton loaders for company detail page
   - Files: Various components

10. **Enhance Company Detail Page**

    - Add "Edit" and "Delete" buttons in header
    - Show relationship count and management
    - Better empty states
    - Files: `frontend/app/company/[nodeId]/page.tsx`

## Technical Details

### Auto-seeding Implementation

- Check if `CompanyModel` table has any records
- If empty, import from `MockGraphRepository` and seed
- Run in startup event, handle errors gracefully

### API Integration Points

- `PUT /api/companies/{company_id}` - Update company
- `DELETE /api/companies/{company_id}` - Delete company
- `PUT /api/relationships/{relationship_id}` - Update relationship
- `DELETE /api/relationships/{relationship_id}` - Delete relationship
- `GET /api/search?query=...` - Backend search

### Files to Modify

- `backend/main.py` - Auto-seed logic
- `frontend/lib/api.ts` - Add update/delete functions
- `frontend/app/page.tsx` - Backend search integration
- `frontend/app/company/[nodeId]/page.tsx` - Edit/delete UI
- `frontend/hooks/useGraphData.ts` - Refresh functionality
- `project1/README.md` - Quick start guide
- New: Startup scripts in root

## Success Criteria

- ✅ Demo can be started with 2 commands (install deps + run script)
- ✅ Database auto-seeds on first run
- ✅ Full CRUD operations available in UI
- ✅ Backend search working
- ✅ Graph refreshes after mutations
- ✅ Professional error handling and loading states
- ✅ Feels like a complete product, not a toy demo

## To-dos

- [ ] Add auto-seeding logic to backend startup event to populate empty database
- [ ] Create cross-platform startup scripts for backend and frontend
- [ ] Add Quick Start section to README with simplified setup instructions
- [ ] Add updateCompany and deleteCompany API functions to frontend/lib/api.ts
- [ ] Add Edit and Delete buttons with forms/modals to company detail page
- [ ] Add relationship edit/delete UI and API functions
- [ ] Replace client-side search with backend /api/search endpoint integration
- [ ] Implement graph auto-refresh after create/update/delete operations
- [ ] Add user-friendly error messages and toast notifications
- [ ] Add loading indicators and skeleton loaders throughout the app

