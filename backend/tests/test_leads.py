from .conftest import auth_headers


# ---------- Flow 1: public capture -> visible to authenticated team ----------

def test_public_lead_capture_flow(client, admin_user):
    resp = client.post("/api/leads/public", json={
        "name": "Jane Prospect",
        "email": "jane@prospect.com",
        "company": "Prospect Co",
        "message": "Interested in the enterprise plan",
    })
    assert resp.status_code == 201
    lead = resp.json()
    assert lead["status"] == "new"
    assert lead["id"]

    # No auth required for submission, but listing IS gated
    headers = auth_headers(client, "admin@test.com", "AdminPass123!")
    listing = client.get("/api/leads", headers=headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["email"] == "jane@prospect.com"


def test_public_capture_rejects_invalid_email(client):
    resp = client.post("/api/leads/public", json={"name": "Bad Email", "email": "not-an-email"})
    assert resp.status_code == 422


# ---------- Flow 2: lifecycle, assignment, notes, activity trail, permissions ----------

def test_member_can_claim_unassigned_lead_and_update_status(client, member_user):
    admin_headers_ignored = None
    # create a lead via public form
    create = client.post("/api/leads/public", json={"name": "Bob Lead", "email": "bob@lead.com"})
    lead_id = create.json()["id"]

    headers = auth_headers(client, "member@test.com", "MemberPass123!")

    # claim it for self
    claim = client.patch(f"/api/leads/{lead_id}", json={"assigned_to_id": member_user.id}, headers=headers)
    assert claim.status_code == 200
    assert claim.json()["assigned_to_id"] == member_user.id

    # now update status since they own it
    status_update = client.patch(f"/api/leads/{lead_id}", json={"status": "contacted"}, headers=headers)
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "contacted"

    # add a note
    note = client.post(f"/api/leads/{lead_id}/notes", json={"content": "Left a voicemail"}, headers=headers)
    assert note.status_code == 201
    assert note.json()["author_email"] == "member@test.com"

    # activity trail recorded creation, assignment, status change, note
    detail = client.get(f"/api/leads/{lead_id}", headers=headers)
    actions = [a["action"] for a in detail.json()["activities"]]
    assert "created" in actions
    assert "assigned" in actions
    assert "status_changed" in actions
    assert "note_added" in actions


def test_member_cannot_reassign_someone_elses_lead(client, member_user, other_member_user):
    create = client.post("/api/leads/public", json={"name": "Carl Lead", "email": "carl@lead.com"})
    lead_id = create.json()["id"]

    member_headers = auth_headers(client, "member@test.com", "MemberPass123!")
    client.patch(f"/api/leads/{lead_id}", json={"assigned_to_id": member_user.id}, headers=member_headers)

    other_headers = auth_headers(client, "other@test.com", "OtherPass123!")
    steal = client.patch(
        f"/api/leads/{lead_id}", json={"assigned_to_id": other_member_user.id}, headers=other_headers
    )
    assert steal.status_code == 403


def test_member_cannot_update_status_on_unassigned_or_others_lead(client, member_user, other_member_user):
    create = client.post("/api/leads/public", json={"name": "Dana Lead", "email": "dana@lead.com"})
    lead_id = create.json()["id"]

    member_headers = auth_headers(client, "member@test.com", "MemberPass123!")
    client.patch(f"/api/leads/{lead_id}", json={"assigned_to_id": member_user.id}, headers=member_headers)

    other_headers = auth_headers(client, "other@test.com", "OtherPass123!")
    resp = client.patch(f"/api/leads/{lead_id}", json={"status": "qualified"}, headers=other_headers)
    assert resp.status_code == 403


def test_admin_can_reassign_and_update_any_lead(client, admin_user, member_user):
    create = client.post("/api/leads/public", json={"name": "Eve Lead", "email": "eve@lead.com"})
    lead_id = create.json()["id"]

    admin_headers = auth_headers(client, "admin@test.com", "AdminPass123!")
    assign = client.patch(
        f"/api/leads/{lead_id}", json={"assigned_to_id": member_user.id}, headers=admin_headers
    )
    assert assign.status_code == 200

    status_update = client.patch(f"/api/leads/{lead_id}", json={"status": "won"}, headers=admin_headers)
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "won"


def test_pagination_and_filtering(client, admin_user):
    for i in range(5):
        client.post("/api/leads/public", json={"name": f"Lead {i}", "email": f"lead{i}@test.com"})

    headers = auth_headers(client, "admin@test.com", "AdminPass123!")
    page1 = client.get("/api/leads?page=1&page_size=2", headers=headers)
    assert page1.status_code == 200
    body = page1.json()
    assert body["total"] == 5
    assert body["pages"] == 3
    assert len(body["items"]) == 2

    search = client.get("/api/leads?search=Lead 3", headers=headers)
    assert search.status_code == 200
    assert search.json()["total"] == 1


def test_get_nonexistent_lead_returns_404(client, admin_user):
    headers = auth_headers(client, "admin@test.com", "AdminPass123!")
    resp = client.get("/api/leads/does-not-exist", headers=headers)
    assert resp.status_code == 404
