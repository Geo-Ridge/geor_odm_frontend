---
title: "Setup Guide"
---


# QGIS ODM Frontend — Setup / Installation

This document explains how to install and configure the **ODM Frontend** plugin for **QGIS**. The plugin provides a graphical interface inside QGIS for running OpenDroneMap/NodeODM processing tasks and importing results directly into your GIS project. :contentReference[oaicite:2]{index=2}

---

## Prerequisites

Before installing the plugin, ensure the following are ready:

### QGIS
Install **QGIS 3.x or later**. You can download installers for your platform from the official QGIS website. :contentReference[oaicite:3]{index=3}

### OpenDroneMap Server
You must have an OpenDroneMap processing server running:

- **NodeODM** (locally or hosted)
- Optionally compatible with a **WebODM** server

NodeODM processes imagery and returns orthophotos, models, DEMs, etc. :contentReference[oaicite:4]{index=4}

---

## Installing the Plugin

You have two installation options:

### A. Manual Installation

1. **Clone or download** this repository:

   ```bash
   git clone https://github.com/Geo-Ridge/geor_odm_frontend.git