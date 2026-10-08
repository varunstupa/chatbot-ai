# Writing a chatbot guide for a screen

The admin app's in-app assistant answers from the guides in this folder. One guide documents one screen (one route). The backend finds the guide from the route the user is on, and only serves guides the user's tenant (and role) is allowed to read.

## How guides get loaded

Every `*.md` file here (except `README.md`) is loaded when the backend starts (`python -m app.main`, or `docker/entrypoint.sh`). There is no upload or sync step.

- New or edited guide: restart the backend. Run `python -m app.knowledge.guide_loader` by hand only while the backend is stopped: Chroma's local store is not safe for two processes, and a running backend would keep a stale index ("Error finding id") until it restarts.
- Unchanged guides are skipped. If only front matter access fields changed (`tenants`, `exclude_tenants`, `roles`, `routes`, `aliases`, `suggested_questions`), the registry is updated without re-embedding. Changing the title or text re-embeds that guide.
- Deleted file: its guide is removed from the store on the next load.
- A guide with an error is reported (`ERROR ...`) and skipped. While any guide has an error, nothing is removed, so a typo cannot take other guides offline. Fix the error and load again.
- `pytest tests/test_app_chat_isolation.py` validates every guide in this folder; run it before committing.

## Workflow when a screen changes

1. Open the screen's component files in the frontend repo (`Frontend/SaaS_Admin`), plus the child components it opens and the labels in `src/assets/i18n/en.json`.
2. Update the guide (or draft a new one with the prompt below).
3. Check the guide against the running screen: every label, rule and error message.
4. Run the tests, then restart the backend (or run the loader).

## File location and front matter

`guides/<module>/<area>/<screen>.md`, starting with:

```yaml
---
doc_id: tms.event-settings.registration   # stable; never reuse for another screen
title: Registration settings page          # how the answer names the screen
routes:
  - tms/event-settings/registration/:event_id
aliases:                                   # names users call this screen
  - registration settings
tenants: all                               # REQUIRED: all, or a list of tenant names
exclude_tenants: []                        # only with tenants: all
roles: []                                  # optional: only these roles (role_name in the login token)
overrides: null                            # base doc_id, for a tenant overlay
suggested_questions:
  - How do I open registration?
source_files:                              # frontend files this guide describes (for reviewers)
  - src/app/modules/tms/registration-settings/registration-settings.component.ts
  - src/app/modules/tms/registration-settings/registration-settings.component.html
---
```

`tenants` has no default. A guide without it is rejected. Each `doc_id` must be unique across the folder.

## Tenant differences

- Same screen for everyone: one guide with `tenants: all`.
- A tenant sees different fields or labels (an environment flag such as `hide_options_for_switz`, or `tenant-label-overrides.json`): add a short overlay guide with `tenants: [switz, test_switz]`, the same `routes`, and `overrides: <base doc_id>`. Describe only what differs. For those tenants the overlay's text is preferred over the base guide.
- A tenant must not see a guide at all: `exclude_tenants: [name]` on the base guide.
- A document that belongs to one tenant: `tenants: [name]`, no `routes`.
- Only some roles may read it: `roles: [admin, event_manager]`. Empty or absent means every role.

## Content rules

- Write for the person using the screen, in on-screen words. No component, variable or API names.
- Quote labels, buttons and error messages exactly as shown.
- One `##` section per topic, and repeat the screen or panel name in every heading. Sections are stored and retrieved separately, so each must make sense alone.
- Keep sections under about 1500 characters. Split longer ones.
- First section: where the screen is and what it is for. Last section: frequently asked questions, each as `**Question?** answer`.
- State rules precisely: what is mandatory, limits, what locks after saving, what a button needs before it is enabled.
- Values that come from the server per organisation (statuses, levels, custom sections) are described as "set up by the organisation", not listed.
- Do not describe anything you could not confirm in the code or on the screen.

## Drafting prompt

> You are documenting one screen of an event management admin app for its in-app help assistant.
> Read the attached component template and code, the child components it opens, and the label list.
> Write a user guide in Markdown following the content rules in guides/README.md: on-screen labels only, exact error messages, one `##` section per topic with the screen name in each heading, sections under 1500 characters, an overview first and an FAQ last.
> Cover every field, button, toggle, dialog, validation rule, state (view/edit, enabled/disabled) and message a user can meet. Note which behaviour depends on an environment flag, and list those separately as candidate tenant overlays.
> Finish with a list of anything you were unsure about so the reviewer can check it.
