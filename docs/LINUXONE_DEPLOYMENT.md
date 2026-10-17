# LinuxONE deployment runbook

This guide is a checklist for deploying PulseGuard Z to an actual LinuxONE Community Cloud virtual server. The account registration, server provisioning, SSH key, and server IP are owner-controlled actions. Do not claim the application is deployed until the health endpoint has been verified on the created server.

## 1. Create and verify your LinuxONE account

1. Open https://linuxone.cloud.marist.edu/#/login and complete registration/activation.
2. Enter event code `SSF2026` if the registration flow asks for it.
3. Create or import an SSH key pair. Keep the **private key on your own device** and never commit it to GitHub or share it in chat.
4. Create a LinuxONE virtual server using the official guide: https://github.com/linuxone-community-cloud/technical-resources/blob/master/faststart/deploy-virtual-server.md
5. Wait until the server status is `ACTIVE`, and record its public IP and selected Linux distribution.

## 2. Connect over SSH

On your own terminal, substitute the actual key path and server IP:

```bash
chmod 600 ~/.ssh/YOUR_PRIVATE_KEY
ssh -i ~/.ssh/YOUR_PRIVATE_KEY linux1@YOUR_SERVER_IP
```

If the official portal specifies a different username or connection command for your instance, follow the portal's instructions.

## 3. Install prerequisites

Use the package manager appropriate for the selected distribution. For a Debian/Ubuntu-like image:

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip
```

For a RHEL/Rocky-like image, use the distribution's supported `dnf` packages for Git and Python instead. If `sudo` or a package is unavailable, follow the image-specific LinuxONE documentation rather than attempting to bypass the restriction.

Check versions:

```bash
python3 --version
git --version
```

## 4. Download and start PulseGuard Z

```bash
git clone https://github.com/Sanjeevakumarnani/PulseGuard-Z-Datathon-2026.git
cd PulseGuard-Z-Datathon-2026
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

Leave the process running in this terminal for the initial verification. In a second SSH session, run:

```bash
curl -fsS http://127.0.0.1:8000/api/health
```

A successful response is JSON containing `"status":"ok"`.

## 5. Open the dashboard securely for a demo

The LinuxONE guide notes that SSH is open by default; do not assume port 8000 is publicly accessible. A safe first option is an SSH tunnel from your local machine, while Uvicorn remains bound to localhost on the server:

```bash
ssh -i ~/.ssh/YOUR_PRIVATE_KEY -L 8000:127.0.0.1:8000 linux1@YOUR_SERVER_IP
```

Then open http://127.0.0.1:8000 on your own computer. If you need a public endpoint, follow the event/cloud policy and configure an approved firewall/reverse-proxy setup; do not expose a development server to the internet without appropriate controls.

## 6. Verification checklist

- [ ] `curl http://127.0.0.1:8000/api/health` returns `status: ok` on the instance
- [ ] Dashboard loads through the approved connection method
- [ ] Inventory, recommendations, and demand scenario load successfully
- [ ] `python -m unittest discover -s tests -v` passes on the instance
- [ ] Record server distribution, Python version, deployment date, and commands
- [ ] Capture genuine screenshots of the instance and live dashboard for the demo
- [ ] Stop the process and release resources according to the cloud/event instructions when finished

## Important limitations

- The seeded inventory is synthetic and the score is a deterministic heuristic.
- This runbook does not provision the cloud account or instance automatically.
- Do not put SSH private keys, cloud credentials, or real patient data in the repository.
- Do not describe the project as LinuxONE-deployed until the above checks succeed on a real instance.
