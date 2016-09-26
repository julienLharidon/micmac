// File Automatically generated by eLiSe
#include "StdAfx.h"
#include "cEqHomogrX.h"


cEqHomogrX::cEqHomogrX():
    cElCompiledFonc(1)
{
   AddIntRef (cIncIntervale("Hom1",0,8));
   AddIntRef (cIncIntervale("Hom2",8,16));
   Close(false);
}



void cEqHomogrX::ComputeVal()
{

  mVal[0] = (mCompCoord[0]*mLocXL1+mCompCoord[1]*mLocYL1+mCompCoord[2])/(mCompCoord[6]*mLocXL1+mCompCoord[7]*mLocYL1+1)-(mCompCoord[8]*mLocXL2+mCompCoord[9]*mLocYL2+mCompCoord[10])/(mCompCoord[14]*mLocXL2+mCompCoord[15]*mLocYL2+1);

}


void cEqHomogrX::ComputeValDeriv()
{
   double tmp0_ = mCompCoord[6];
   double tmp1_ = tmp0_*mLocXL1;
   double tmp2_ = mCompCoord[7];
   double tmp3_ = tmp2_*mLocYL1;
   double tmp4_ = tmp1_+tmp3_;
   double tmp5_ = tmp4_+1;
   double tmp6_ = ElSquare(tmp5_);
   double tmp7_ = mCompCoord[0];
   double tmp8_ = tmp7_*mLocXL1;
   double tmp9_ = mCompCoord[1];
   double tmp10_ = tmp9_*mLocYL1;
   double tmp11_ = tmp8_+tmp10_;
   double tmp12_ = mCompCoord[2];
   double tmp13_ = tmp11_+tmp12_;
   double tmp14_ = mCompCoord[14];
   double tmp15_ = tmp14_*mLocXL2;
   double tmp16_ = mCompCoord[15];
   double tmp17_ = tmp16_*mLocYL2;
   double tmp18_ = tmp15_+tmp17_;
   double tmp19_ = tmp18_+1;
   double tmp20_ = ElSquare(tmp19_);
   double tmp21_ = mCompCoord[8];
   double tmp22_ = tmp21_*mLocXL2;
   double tmp23_ = mCompCoord[9];
   double tmp24_ = tmp23_*mLocYL2;
   double tmp25_ = tmp22_+tmp24_;
   double tmp26_ = mCompCoord[10];
   double tmp27_ = tmp25_+tmp26_;

  mVal[0] = (tmp13_)/(tmp5_)-(tmp27_)/(tmp19_);

  mCompDer[0][0] = (mLocXL1*(tmp5_))/tmp6_;
  mCompDer[0][1] = (mLocYL1*(tmp5_))/tmp6_;
  mCompDer[0][2] = (tmp5_)/tmp6_;
  mCompDer[0][3] = 0;
  mCompDer[0][4] = 0;
  mCompDer[0][5] = 0;
  mCompDer[0][6] = -((tmp13_)*mLocXL1)/tmp6_;
  mCompDer[0][7] = -((tmp13_)*mLocYL1)/tmp6_;
  mCompDer[0][8] = -((mLocXL2*(tmp19_))/tmp20_);
  mCompDer[0][9] = -((mLocYL2*(tmp19_))/tmp20_);
  mCompDer[0][10] = -((tmp19_)/tmp20_);
  mCompDer[0][11] = 0;
  mCompDer[0][12] = 0;
  mCompDer[0][13] = 0;
  mCompDer[0][14] = -(-((tmp27_)*mLocXL2)/tmp20_);
  mCompDer[0][15] = -(-((tmp27_)*mLocYL2)/tmp20_);
}


void cEqHomogrX::ComputeValDerivHessian()
{
  ELISE_ASSERT(false,"Foncteur cEqHomogrX Has no Der Sec");
}

void cEqHomogrX::SetXL1(double aVal){ mLocXL1 = aVal;}
void cEqHomogrX::SetXL2(double aVal){ mLocXL2 = aVal;}
void cEqHomogrX::SetYL1(double aVal){ mLocYL1 = aVal;}
void cEqHomogrX::SetYL2(double aVal){ mLocYL2 = aVal;}



double * cEqHomogrX::AdrVarLocFromString(const std::string & aName)
{
   if (aName == "XL1") return & mLocXL1;
   if (aName == "XL2") return & mLocXL2;
   if (aName == "YL1") return & mLocYL1;
   if (aName == "YL2") return & mLocYL2;
   return 0;
}


cElCompiledFonc::cAutoAddEntry cEqHomogrX::mTheAuto("cEqHomogrX",cEqHomogrX::Alloc);


cElCompiledFonc *  cEqHomogrX::Alloc()
{  return new cEqHomogrX();
}


