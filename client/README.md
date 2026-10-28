# IT Support Assistant Web (multi-tenant, RAG-backed chat)
```
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL
npm install && npm run dev   # http://localhost:3000
```
Backend must allow CORS from http://localhost:3000 (FastAPI CORSMiddleware).
Users whose membership role is `admin` or `owner` see /admin; everyone else lands in /chat.

## Roles and areas
- Super-admin (`is_super_admin: true` on sign-in, or a `super_admin` membership): /platform (all tenants), and can open any /admin/{orgId}.
- Org admin (`admin`/`owner` membership): /admin/{orgId} — knowledge bases and members.
- Member: /chat only.

## Endpoints the Members page expects
GET    /organizations/{id}/members            -> [{user_id, name, email, role, status}]
POST   /organizations/{id}/members            {email, role}   (invite)
PATCH  /organizations/{id}/members/{user_id}  {role}
DELETE /organizations/{id}/members/{user_id}
GET /organizations/ must return every tenant for a super-admin.

## Sign-up
Anyone can register at /register. POST /auth/ should create the user's own organization and an `admin` membership, so the sign-in response lists it. New users land in /admin/{orgId} (setup checklist); the sidebar links to Assistant and Admin.
If the account has no organization, /chat offers a "Create workspace" step (POST /organizations/, then /auth/refresh to pick up the new membership).

## Multiple organizations
A user can belong to several. The sidebar switcher sets the active organization (stored in localStorage as `sa_org`).
Chat sends `organization_id` in the body of POST /api/v1/chat and /chat/stream, and as `?organization_id=` on GET /api/v1/chat/conversations.
The backend must verify the user is a member of that organization.
