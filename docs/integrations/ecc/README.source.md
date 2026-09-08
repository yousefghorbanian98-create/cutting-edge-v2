<p align="center">
  <img src="assets/hero.png" alt="ECC - the agent harness operating system" width="100%" />
</p>

<p align="center">
  <a href="https://www.star-history.com/affaan-m/ecc">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=affaan-m/ECC&type=trending&theme=dark" />
      <img src="https://api.star-history.com/badge?repo=affaan-m/ECC&type=trending" alt="GitHub Trending Repository of the Day" height="46" />
    </picture>
  </a>
  <a href="https://www.star-history.com/affaan-m/ecc">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=affaan-m/ECC&type=rank&theme=dark" />
      <img src="https://api.star-history.com/badge?repo=affaan-m/ECC&type=rank" alt="Star History Global Rank" height="46" />
    </picture>
  </a>
</p>

<p align="center">
  <strong>Language:</strong>
  <a href="README.md">English</a> |
  <a href="docs/pt-BR/README.md">Português (Brasil)</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="docs/zh-TW/README.md">繁體中文</a> |
  <a href="docs/ja-JP/README.md">日本語</a> |
  <a href="docs/ko-KR/README.md">한국어</a> |
  <a href="docs/tr/README.md">Türkçe</a> |
  <a href="docs/ru/README.md">Русский</a> |
  <a href="docs/vi-VN/README.md">Tiếng Việt</a> |
  <a href="docs/th/README.md">ไทย</a> |
  <a href="docs/de-DE/README.md">Deutsch</a> |
  <a href="docs/es/README.md">Español</a> |
  <a href="docs/uk-UA/README.md">Українська</a>
</p>

<p align="center">
  <a href="https://discord.gg/36yGMHGFbR"><img src="https://img.shields.io/discord/1496644400590094540?logo=discord&logoColor=white&label=Discord&color=5865F2" alt="Discord" /></a>
  <a href="https://ecc.tools"><img src="https://img.shields.io/badge/Website-ecc.tools-E07856?logo=googlechrome&logoColor=white" alt="Website" /></a>
  <a href="https://github.com/apps/ecc-tools"><img src="https://img.shields.io/badge/GitHub%20App-ECC%20Tools-181717?logo=github&logoColor=white" alt="GitHub App" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license" /></a>
</p>

<p align="center">
  <a href="https://github.com/affaan-m/ECC/stargazers"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.ecc.tools%2Fbadge%2Fstars&style=flat" alt="Stars" /></a>
  <a href="https://github.com/affaan-m/ECC/network/members"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.ecc.tools%2Fbadge%2Fforks&style=flat" alt="Forks" /></a>
  <a href="https://github.com/affaan-m/ECC/graphs/contributors"><img src="https://img.shields.io/github/contributors/affaan-m/ECC?style=flat" alt="Contributors" /></a>
  <a href="https://github.com/marketplace/ecc-tools"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.ecc.tools%2Fbadge%2Finstalls&logo=github" alt="GitHub App installs" /></a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/ecc-universal"><img src="https://img.shields.io/npm/dw/ecc-universal?label=ecc-universal&logo=npm" alt="ecc-universal npm downloads" /></a>
  <a href="https://www.npmjs.com/package/ecc-agentshield"><img src="https://img.shields.io/npm/dw/ecc-agentshield?label=ecc-agentshield&logo=npm" alt="ecc-agentshield npm downloads" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/-Shell-4EAA25?logo=gnu-bash&logoColor=white" alt="Shell" />
  <img src="https://img.shields.io/badge/-TypeScript-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/-Go-00ADD8?logo=go&logoColor=white" alt="Go" />
  <img src="https://img.shields.io/badge/-Java-ED8B00?logo=openjdk&logoColor=white" alt="Java" />
  <img src="https://img.shields.io/badge/-Perl-39457E?logo=perl&logoColor=white" alt="Perl" />
  <img src="https://img.shields.io/badge/-Markdown-000000?logo=markdown&logoColor=white" alt="Markdown" />
</p>

> [!WARNING]
> **Official sources only.** Install ECC only from verified channels: the GitHub repository [github.com/affaan-m/ECC](https://github.com/affaan-m/ECC), the npm packages [`ecc-universal`](https://www.npmjs.com/package/ecc-universal) and [`ecc-agentshield`](https://www.npmjs.com/package/ecc-agentshield), the [GitHub App](https://github.com/apps/ecc-tools), the plugin slug `ecc@ecc`, and the project website [ecc.tools](https://ecc.tools). Third-party re-uploads and unofficial mirrors are not maintained or reviewed by the project and may contain malware.

## Install with Claude Code

Run the canonical guided setup from your terminal:

```bash
npx ecc-universal setup
```

If npm reports a version or cache error, confirm the registry version before retrying:

```bash
npm view ecc-universal version
```

This path requires Node.js 18 or newer, Git, and Claude Code 2.1 or newer on
`PATH`. It safely installs, updates, or moves one `ecc@ecc` plugin scope and
records the hook profile you choose.

Alternatively, run Claude Code's native plugin commands inside Claude Code:

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

The native path installs ECC's skills, agents, commands, and plugin-managed hooks. If you choose it, stop there. Do not also run a full manual install into Claude Code.

> Both paths install the same `ecc@ecc` plugin. Choose one and do not stack
> another manual Claude install on top.

<div align="center">

