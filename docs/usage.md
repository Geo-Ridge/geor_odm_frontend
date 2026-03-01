---
title: "Usage Guide"
---


# QGIS ODM Frontend — User Guide

This document describes how to use the **ODM Frontend** plugin in **QGIS** to process drone imagery with an OpenDroneMap server and import results into your map project. :contentReference[oaicite:7]{index=7}

---

## 1. Launch the Plugin

After installation:

1. Open **QGIS**.
2. Go to **Plugins → ODM Frontend → ODM Frontend**  
   or click the plugin icon if visible in the toolbar. :contentReference[oaicite:8]{index=8}

---

## 2. Configure Your Server Connection

1. In the plugin dialog, locate the **Connection or Settings** panel.
2. Enter the URL for your running NodeODM/WebODM server.  
   Example: `http://localhost:3000`
3. Add an API token if your server requires authentication.
4. Click **Test Connection** to ensure the server is reachable. :contentReference[oaicite:9]{index=9}

---

## 3. Start a New Processing Job

### A. Add Images

1. Switch to the **Processing** tab.
2. Click **Add Images** and select your drone image files (e.g., JPEG, PNG). :contentReference[oaicite:10]{index=10}

---

### B. Configure Processing Options

1. Select a **processing preset** (e.g., Default, High Resolution, Fast Orthophoto).
2. Adjust advanced options such as:
   - Reconstruction quality
   - Camera lens correction
   - Output types (DSM, DTM, textured mesh)
   - Thread count and memory limits :contentReference[oaicite:11]{index=11}

---

### C. (Optional) Add Ground Control Points (GCPs)

1. Switch to the **GCPs** tab.
2. Load or create GCP entries using the supported GCP file format.
   - Format includes geographic and pixel coordinates. :contentReference[oaicite:12]{index=12}

---

## 4. Run and Monitor the Job

1. Click **Create Task & Start Processing**.
2. Enter a task name if prompted.
3. Monitor job progress in the **Tasks** or **Status** panel. :contentReference[oaicite:13]{index=13}

---

## 5. Download and Import Results

Once processing finishes:

1. In the **Results** section, click **Download Results**. :contentReference[oaicite:14]{index=14}
2. Use **Import to QGIS** to automatically load:
   - Orthophotos
   - DEM/DSM layers
   - Point clouds
   - Textured 3D models

QGIS will load result files with proper CRS settings if available. :contentReference[oaicite:15]{index=15}

---

## Tips & Common Tasks

- Always check that your drone images are georeferenced or include metadata for correct processing. :contentReference[oaicite:16]{index=16}
- Larger datasets may require high memory or longer processing times.
- Use NodeODM logs for debugging failed jobs.

---

## Troubleshooting

### ❗ Cannot Connect to Server

- Ensure NodeODM/WebODM is running and listening on the specified port. :contentReference[oaicite:17]{index=17}

### ❗ Errors on Import

- Confirm output CRS matches your QGIS project CRS. :contentReference[oaicite:18]{index=18}

### ❗ Poor Results

- Add **GCPs** or enhance image overlap settings for better accuracy. :contentReference[oaicite:19]{index=19}