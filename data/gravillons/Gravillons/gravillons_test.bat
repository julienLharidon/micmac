set BIN_DIR=%1
set CHANT_DIR=%2

"%BIN_DIR%Tapioca" MulScale "%CHANT_DIR%.*.JPG" 500 1500
"%BIN_DIR%Tapas" FraserBasic "%CHANT_DIR%.*.JPG" Out=Arbitrary
"%BIN_DIR%GCPBascule" "%CHANT_DIR%.*.JPG" Arbitrary Ground_Init Dico-Appuis.xml Mesure-Appuis.xml
"%BIN_DIR%Campari" "%CHANT_DIR%.*.JPG" Ground_Init Ground
"%BIN_DIR%AperiCloud" "%CHANT_DIR%.*.JPG" Ground Out=Apericloud.ply
"%BIN_DIR%Malt" GeomImage "%CHANT_DIR%.*.JPG" Ground Master=1.JPG ZoomF=2
"%BIN_DIR%Nuage2Ply" "%CHANT_DIR%MM-Malt-Img-1/NuageImProf_STD-MALT_Etape_7.xml" "Attr=%CHANT_DIR%1.JPG" "Out=%CHANT_DIR%1.ply" RatioAttrCarte=2
