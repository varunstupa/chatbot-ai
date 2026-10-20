---
doc_id: tms.event-settings.documents-sponsors
title: Documents & Sponsors page
routes:
  - tms/event-settings/document-sponsors/:event_id
aliases:
  - documents
  - sponsors
  - sponsor logos
  - partners
  - partner logos
  - documents and sponsors
tenants: all
exclude_tenants: []
overrides: null
suggested_questions:
  - How do I show a document on OTT?
  - What file types can I upload?
  - How do I change the order of sponsor logos?
  - Does unpublishing delete the sponsor logos?
backend_sources:
  - gateway/src/routers/events_router.py (update_documents, update_sponsors; Event Access permission)
  - tms/src/crud/events_crud.py (update_documents, update_sponsors)
source_files:
  - src/app/modules/tms/event-documents-sponsors/event-documents-sponsors.component.ts
  - src/app/modules/tms/event-documents-sponsors/event-documents-sponsors.component.html
---
# Documents & Sponsors page – user guide

This guide describes the **Documents & Sponsors** step of an event in the Stupa Event Management System (admin panel). Here the organiser uploads event documents and sponsor and partner logos, and publishes them to OTT (the public event viewing app).

## Where to find it

Open **Event** from the sidebar, then click **Documents & Sponsors** in the row of setup steps at the top of the page.

## Documents & Sponsors page: where it is and what it is for

- Page address: `/tms/event-settings/document-sponsors/<event id>`, for example `/tms/event-settings/document-sponsors/534`.
- It is the **Documents & Sponsors** step in the row of event setup steps.
- Three tabs:
  - **Documents** – "Upload documents that you want to show on OTT" (for example prospectus, rules).
  - **Sponsor** – "Upload logo that you want to show on OTT".
  - **Partners** – "Upload logo that you want to show on OTT".
- Uploaded items are only visible on OTT after they are **published**.

## Documents tab: uploading and managing documents

- **Upload Documents**: click **Choose file** or drag and drop files. Supported formats: **PDF, DOCX**, maximum **10 MB** per file.
- The files are saved after upload: "Document Saved Successfully".
- **Uploaded Documents** lists them ("No documents uploaded yet." when empty).
- Drag a document to change the order: "Order updated successfully".
- Per document:
  - **View Document** opens it in a new tab ("Popup blocked. Please allow popups for this site." means the browser blocked it).
  - Rename it in **Uploaded Files**: change **File Name** and click **Save**.
  - **Delete** asks "Delete Document" – "Are you sure you want to delete the document ?". Confirm to delete: "Documents Deleted successfully".

## Sponsor and Partners tabs: uploading logos

- **Upload Sponsors Logo** / **Upload Partners Logo**: click **Choose file** or drag and drop. Supported: **JPEG, PNG**, maximum **2 MB** per file.
- Logos are saved after upload: "Logos saved successfully".
- **Uploaded Logo** shows them. Drag to change the order shown on OTT ("Order updated successfully").
- Click the × on a logo to delete it. It asks "Delete Sponsor Logo" / "Delete Partner Logo" – "Are you sure you want to delete the sponsor/partner logo ?". Confirm: "Logo Deleted successfully".

## Publishing to OTT

- Each tab has a **Publish** toggle (shown when the tab has items).
- Switching it on publishes **all items of that tab**: "Document Published Successfully", "Sponsor Published Successfully", "Partner Published Successfully".
- Switching it off unpublishes all items of that tab: "Document Unpublished Successfully", "Sponsors Unpublished Successfully", "Partner Unpublished Successfully". **Unpublishing does not delete the files or logos**; they stay in the list and can be published again.
- Documents, sponsors and partners are published separately.

## Upload errors and what they mean

- `"<file name>" is not allowed.` – wrong file type (documents: PDF or DOCX; logos: JPEG or PNG).
- `"<file name>" exceeds max size limit.` – the file is too large (documents 10 MB, logos 2 MB).
- When one file in a multi-file upload has one of these errors, **none** of the files is uploaded. Remove that file and upload again.
- "One of the files failed to upload." / "File upload failed" – try again.
- "Please select a valid event before uploading files" – open the page from an event.
- Saving needs **Edit** permission on **Event Access**; otherwise "Access Denied".

## Frequently asked questions about the Documents & Sponsors page

**How do I show a document on OTT?** Upload it on the **Documents** tab and turn on **Publish**.

**What file types can I upload?** Documents: PDF or DOCX up to 10 MB. Sponsor and partner logos: JPEG or PNG up to 2 MB.

**How do I change the order of sponsor logos?** Drag the logos into the order you want on the **Sponsor** tab.

**Does unpublishing delete the sponsor logos?** No. They are only hidden from OTT.

**Can I publish only one sponsor?** No. Publish applies to all logos of the tab.

**How do I rename a document?** Open the document's rename option in **Uploaded Files**, change **File Name**, click **Save**.

**Why is my 4 MB logo refused?** Logos are limited to 2 MB ("exceeds max size limit"). Documents may be up to 10 MB.
