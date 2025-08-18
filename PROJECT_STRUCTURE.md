## Project Structure ✨

<!-- START_STRUCTURE -->
```
├── LICENSE
├── PROJECT_STRUCTURE.md
├── README.md
├── backend/
│   ├── README.md
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── LICENSE
│   │   ├── README.md
│   │   ├── ats_test.json
│   │   ├── main.py
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── resume_test.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── app.py
│   │   │   ├── streamlit_app.py
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       ├── ats/
│   │   │       │   ├── __init__.py
│   │   │       │   └── analyzer.py
│   │   │       ├── data_extractor/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── core.py
│   │   │       │   └── utils.py
│   │   │       ├── llm/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py
│   │   │       │   ├── manager.py
│   │   │       │   └── providers/
│   │   │       │       ├── __init__.py
│   │   │       │       └── gemini.py
│   │   │       ├── parser/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── core.py
│   │   │       │   ├── enhanced.py
│   │   │       │   └── field_extractor.py
│   │   │       └── resume_generator/
│   │   │           ├── __init__.py
│   │   │           ├── core.py
│   │   │           └── templates.py
│   │   ├── startup.sh
│   │   └── uv.lock
│   ├── local_mcp/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── server.py
│   ├── mcp/
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   └── uv.lock
│   ├── resume_mcp/
│   │   └── resume_server.py
│   └── sample_mcp.py
└── frontend/
    ├── README.md
    ├── app/
    │   ├── about/
    │   │   └── page.tsx
    │   ├── dashboard/
    │   │   ├── components/
    │   │   │   └── card.tsx
    │   │   └── page.tsx
    │   ├── generate-resume/
    │   │   └── page.tsx
    │   ├── globals.css
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── resume-editor/
    │   │   └── page.tsx
    │   ├── sign-in/
    │   │   └── [[...sign-in]]/
    │   │       └── page.tsx
    │   ├── sign-up/
    │   │   └── [[...sign-up]]/
    │   │       └── page.tsx
    │   └── templates/
    │       ├── ClassicResume.tsx
    │       ├── CreativeResume.tsx
    │       ├── ModernResume.tsx
    │       └── page.tsx
    ├── components/
    │   ├── animated-group.tsx
    │   ├── feature-card.tsx
    │   ├── footer.tsx
    │   ├── header.tsx
    │   ├── hero-section.tsx
    │   ├── logo.tsx
    │   ├── main/
    │   │   ├── header.tsx
    │   │   └── sidebar.tsx
    │   ├── text-effect.tsx
    │   └── ui/
    │       ├── button.tsx
    │       ├── card.tsx
    │       ├── input.tsx
    │       └── label.tsx
    ├── components.json
    ├── data/
    │   └── resume-schema.json
    ├── eslint.config.mjs
    ├── lib/
    │   └── utils.ts
    ├── middleware.ts
    ├── next.config.ts
    ├── package-lock.json
    ├── package.json
    ├── pnpm-lock.yaml
    ├── postcss.config.mjs
    ├── public/
    │   ├── Hero Gradients_001.png
    │   ├── bg.jpg
    │   ├── favicon.ico
    │   ├── file.svg
    │   ├── globe.svg
    │   ├── hero-gradient.png
    │   ├── logo.png
    │   ├── next.svg
    │   ├── vercel.svg
    │   └── window.svg
    ├── tsconfig.json
    ├── types/
    │   └── resume.ts
    └── vercel.json
```
<!-- END_STRUCTURE -->