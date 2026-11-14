VOICE CONTROL ASSISTANT - HOSTING FILES

1) GitHub Pages
- Copy docs/index.html into your existing repository at docs/index.html.
- Commit and push.
- Open repository Settings > Pages.
- Under Build and deployment choose "Deploy from a branch".
- Select branch main and folder /docs, then Save.
- Wait for the Pages deployment workflow. Expected URL:
  https://shivamgupta4469.github.io/Voice-Control-Assistant/

2) Render dashboard
- Copy the render-dashboard folder AND the root render.yaml into the root of your existing GitHub repository.
- In Render choose New > Blueprint and connect the Voice-Control-Assistant repository.
- Render should detect the root render.yaml. Confirm and deploy.
- The service uses render-dashboard as its root directory and /health as its health check.

IMPORTANT
This Render service is a lightweight information/status dashboard only.
It does not host or remotely control the Windows desktop assistant. Microphone,
local files, screen OCR and Ollama remain on the user's own computer.
