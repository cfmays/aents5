# Deploying AENTS

Production runs on a DigitalOcean droplet: **gunicorn** (systemd) behind **nginx**,
SQLite database, Let's Encrypt TLS.

## Server layout

| | |
|---|---|
| Host | `charley@167.172.135.242` (`ubuntu-s-1vcpu-1gb-nyc1-01`) |
| Site | https://aents.charleymays.org |
| Project dir | `/home/charley/aents5` |
| Virtualenv | `/home/charley/aents-venv` |
| Env vars | `/home/charley/aents.env` (defines `DJANGO_SECRET_KEY`) |
| App server | `gunicorn.service` + `gunicorn.socket` -> `/run/gunicorn.sock` (3 workers, runs as `charley:www-data`) |
| Web server | `/etc/nginx/sites-enabled/aents.charleymays.org` |
| Static files | collected to `/home/charley/aents5/static/`, served by nginx at `/static/` |
| Python | pyenv 3.11.9 (use the venv binaries directly) |

`db.sqlite3` is git-ignored and lives only on the server, so deploys never touch it.

The same droplet hosts two unrelated apps: `entsgunicorn.service` (ents.charleymays.org)
and `gsc-schedule.service` (keeps.charleymays.org). Leave those alone.

## Deploy an update

SSH in:

```bash
ssh charley@167.172.135.242
cd /home/charley/aents5
source /home/charley/aents-venv/bin/activate   # so "python" = the venv's python
```

1. **Back up the database**

   ```bash
   python manage.py dumpdata > aents_db_bkup_$(date +%m_%d_%Y).json
   ```

2. **Check the working tree is clean, then pull**

   ```bash
   git status          # expect "nothing to commit, working tree clean"
   git pull origin main
   ```

3. **Install dependencies** (a no-op when requirements.txt hasn't changed)

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Collect static files**

   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Restart gunicorn** (nginx only needs a reload if its config changed)

   ```bash
   sudo systemctl restart gunicorn
   ```

7. **Verify**

   ```bash
   sudo systemctl status gunicorn --no-pager
   curl -I https://aents.charleymays.org
   ```

   Then load the site and click through New Encounter / Update Encounter.

## Change the "What's new" pop-up

Each logged-in user sees the pop-up once, the next time they load any page. The
app records who has seen it in the `AnnouncementSeen` table.

Two files control it:

| File | What it holds |
|---|---|
| `encounters/templates/encounters/announcement.html` | The title and message text (plain HTML) |
| `encounters/templatetags/announcement.py` | `CURRENT_ANNOUNCEMENT`, the name of the current message |

To post a new message:

1. **On your Mac**, edit the title (`What's new`) and the text inside
   `<div class="modal-body">` in `announcement.html`.
2. In `announcement.py`, change `CURRENT_ANNOUNCEMENT` to a new name you haven't
   used before, e.g. `'2027-03-new-animals'`. **This is what makes everyone see
   it again.** If you only edit the text and keep the old name, users who saw the
   old message won't see the new one.
3. Test it locally (`DEBUG=True python manage.py runserver`, then log in).
   To see it again while testing, run:

   ```bash
   python manage.py shell -c "from encounters.models import AnnouncementSeen; AnnouncementSeen.objects.all().delete()"
   ```

   Only run that locally; on the server it would make everyone see the current
   message again.
4. Commit, push, and follow "Deploy an update" above. No new migration is
   needed, but the gunicorn restart (step 6) is, since `announcement.py` is
   Python code.

To stop showing a message to anyone (including users added later), delete
the `{% show_announcement %}` line near the bottom of
`encounters/templates/base_generic.html`. Put it back when you have a new
message.

## Rollback

```bash
cd /home/charley/aents5
source /home/charley/aents-venv/bin/activate
git log --oneline -5            # pick the previous good commit
git reset --hard <commit>
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

Restore data from a backup dump if a bad migration corrupted it:

```bash
python manage.py loaddata aents_db_bkup_MM_DD_YYYY.json
```

## Troubleshooting

```bash
# app logs: gunicorn access lines, errors, Django tracebacks
sudo journalctl -u gunicorn -n 100 --no-pager
sudo journalctl -u gunicorn -f

# nginx
sudo tail -n 50 /var/log/nginx/error.log
sudo nginx -t

# 502 Bad Gateway usually means gunicorn is down or the socket is stale
sudo systemctl restart gunicorn.socket gunicorn
```

If you edited `gunicorn.service` or `gunicorn.socket`:

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn.socket gunicorn
```

If you edited the nginx site config:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

## Environment / secrets

`/home/charley/aents.env` must define `DJANGO_SECRET_KEY` (exact spelling; Django
falls back to a random key otherwise, which logs everyone out on each restart).
`DEBUG` is not set, so it defaults to `False`, which is what selects the production
`ALLOWED_HOSTS` and `STATIC_ROOT` in `aents5/settings.py`.

## TLS

Certbot auto-renews via its systemd timer. Nothing to do on deploy. Check with:

```bash
sudo certbot certificates
```

## First-time setup on a fresh box

See the "Setup a new instance" section in `README.md` for the migrate /
createsuperuser / loaddata steps, then create the systemd units and nginx site
shown in the tables above.
