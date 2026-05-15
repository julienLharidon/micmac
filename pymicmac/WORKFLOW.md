# MicMac v1 Workflow Trace

1. **Tapioca** (Tie-point extraction)
   - Command: `Tapioca All "IMG_.*JPG" 1000`
   - Action: Extracts SIFT-like features, matches them, and saves as binary `.dat` files in `Homol/` directory.

2. **Tapas** (Orientation/Bundle Adjustment)
   - Command: `Tapas RadialStd "IMG_.*JPG" Out=Ori-All`
   - Action: Solves for internal and external orientation using a specific camera model (e.g., RadialStd). Produces XML files in `Ori-All/`.

3. **Malt** (Dense Correlation)
   - Command: `Malt Ortho "IMG_.*JPG" Ori-All`
   - Action: Performs dense matching to produce depth maps.

4. **Tawny** (Radiometric Balancing)
   - Command: `Tawny "Ortho-Malt/"`
   - Action: Balances radiometry between images for a seamless ortho-mosaic.

5. **Nuage2Ply** (3D Cloud Generation)
   - Command: `Nuage2Ply "Malt/Nuage.xml" Attr="Ortho.tif" Out=Cloud.ply`
   - Action: Converts depth maps to a colorized point cloud in PLY format.
