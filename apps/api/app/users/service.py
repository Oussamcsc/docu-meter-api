from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.organizations.models import Organization
from app.projects.models import Project
from app.users.models import OrganizationMembership, User


@dataclass(frozen=True)
class SyncedUserWorkspace:
    user: User
    organization: Organization
    project: Project
    created: bool


def build_default_org_name(*, name: str | None, email: str) -> str:
    display_name = (name or email.split("@", 1)[0]).strip()
    if not display_name:
        display_name = "User"
    return f"{display_name}'s Org"


def ensure_user_workspace(
    db: Session,
    *,
    clerk_id: str,
    email: str,
    name: str | None = None,
) -> SyncedUserWorkspace:
    user = db.query(User).filter(User.clerk_id == clerk_id).one_or_none()
    if user is not None:
        if user.email != email:
            user.email = email
            db.add(user)
            db.commit()
            db.refresh(user)

        if user.current_org_id is None or user.current_project_id is None:
            return _provision_workspace_for_existing_user(db, user=user, name=name)

        organization = db.get(Organization, user.current_org_id)
        project = db.get(Project, user.current_project_id)
        if organization is None or project is None:
            return _provision_workspace_for_existing_user(db, user=user, name=name)

        return SyncedUserWorkspace(user=user, organization=organization, project=project, created=False)

    organization = Organization(name=build_default_org_name(name=name, email=email))
    db.add(organization)
    db.flush()

    project = Project(organization_id=organization.id, name="Default Project")
    db.add(project)
    db.flush()

    user = User(
        clerk_id=clerk_id,
        email=email,
        current_org_id=organization.id,
        current_project_id=project.id,
    )
    db.add(user)
    db.flush()

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=organization.id,
        role="owner",
    )
    db.add(membership)
    db.commit()
    db.refresh(user)
    db.refresh(organization)
    db.refresh(project)

    return SyncedUserWorkspace(user=user, organization=organization, project=project, created=True)


def _provision_workspace_for_existing_user(
    db: Session,
    *,
    user: User,
    name: str | None,
) -> SyncedUserWorkspace:
    organization = Organization(name=build_default_org_name(name=name, email=user.email))
    db.add(organization)
    db.flush()

    project = Project(organization_id=organization.id, name="Default Project")
    db.add(project)
    db.flush()

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=organization.id,
        role="owner",
    )
    db.add(membership)
    user.current_org_id = organization.id
    user.current_project_id = project.id
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(organization)
    db.refresh(project)

    return SyncedUserWorkspace(user=user, organization=organization, project=project, created=False)
