// File Automatically generated by eLiSe
#include "StdAfx.h"
#include "cGen2DBundleAttach_Deg2.h"


cGen2DBundleAttach_Deg2::cGen2DBundleAttach_Deg2():
    cElCompiledFonc(2)
{
   AddIntRef (cIncIntervale("CX",0,6));
   AddIntRef (cIncIntervale("CY",6,12));
   Close(false);
}



void cGen2DBundleAttach_Deg2::ComputeVal()
{
   double tmp0_ = mLocPFixV_y-mLocCentrFixV_y;
   double tmp1_ = (tmp0_)/mLocAmplFixV;
   double tmp2_ = mLocPFixV_x-mLocCentrFixV_x;
   double tmp3_ = (tmp2_)/mLocAmplFixV;
   double tmp4_ = ElSquare(tmp1_);
   double tmp5_ = ElSquare(tmp3_);

  mVal[0] = (mCompCoord[0]+mCompCoord[1]*(tmp1_)+mCompCoord[2]*(tmp3_)+mCompCoord[3]*tmp4_+mCompCoord[4]*(tmp3_)*(tmp1_)+mCompCoord[5]*tmp5_)-mLocFixedV_x;

  mVal[1] = (mCompCoord[6]+mCompCoord[7]*(tmp1_)+mCompCoord[8]*(tmp3_)+mCompCoord[9]*tmp4_+mCompCoord[10]*(tmp3_)*(tmp1_)+mCompCoord[11]*tmp5_)-mLocFixedV_y;

}


void cGen2DBundleAttach_Deg2::ComputeValDeriv()
{
   double tmp0_ = mLocPFixV_y-mLocCentrFixV_y;
   double tmp1_ = (tmp0_)/mLocAmplFixV;
   double tmp2_ = mLocPFixV_x-mLocCentrFixV_x;
   double tmp3_ = (tmp2_)/mLocAmplFixV;
   double tmp4_ = ElSquare(tmp1_);
   double tmp5_ = ElSquare(tmp3_);
   double tmp6_ = (tmp3_)*(tmp1_);

  mVal[0] = (mCompCoord[0]+mCompCoord[1]*(tmp1_)+mCompCoord[2]*(tmp3_)+mCompCoord[3]*tmp4_+mCompCoord[4]*(tmp3_)*(tmp1_)+mCompCoord[5]*tmp5_)-mLocFixedV_x;

  mCompDer[0][0] = 1;
  mCompDer[0][1] = tmp1_;
  mCompDer[0][2] = tmp3_;
  mCompDer[0][3] = tmp4_;
  mCompDer[0][4] = tmp6_;
  mCompDer[0][5] = tmp5_;
  mCompDer[0][6] = 0;
  mCompDer[0][7] = 0;
  mCompDer[0][8] = 0;
  mCompDer[0][9] = 0;
  mCompDer[0][10] = 0;
  mCompDer[0][11] = 0;
  mVal[1] = (mCompCoord[6]+mCompCoord[7]*(tmp1_)+mCompCoord[8]*(tmp3_)+mCompCoord[9]*tmp4_+mCompCoord[10]*(tmp3_)*(tmp1_)+mCompCoord[11]*tmp5_)-mLocFixedV_y;

  mCompDer[1][0] = 0;
  mCompDer[1][1] = 0;
  mCompDer[1][2] = 0;
  mCompDer[1][3] = 0;
  mCompDer[1][4] = 0;
  mCompDer[1][5] = 0;
  mCompDer[1][6] = 1;
  mCompDer[1][7] = tmp1_;
  mCompDer[1][8] = tmp3_;
  mCompDer[1][9] = tmp4_;
  mCompDer[1][10] = tmp6_;
  mCompDer[1][11] = tmp5_;
}


void cGen2DBundleAttach_Deg2::ComputeValDerivHessian()
{
  ELISE_ASSERT(false,"Foncteur cGen2DBundleAttach_Deg2 Has no Der Sec");
}

void cGen2DBundleAttach_Deg2::SetAmplFixV(double aVal){ mLocAmplFixV = aVal;}
void cGen2DBundleAttach_Deg2::SetCentrFixV_x(double aVal){ mLocCentrFixV_x = aVal;}
void cGen2DBundleAttach_Deg2::SetCentrFixV_y(double aVal){ mLocCentrFixV_y = aVal;}
void cGen2DBundleAttach_Deg2::SetFixedV_x(double aVal){ mLocFixedV_x = aVal;}
void cGen2DBundleAttach_Deg2::SetFixedV_y(double aVal){ mLocFixedV_y = aVal;}
void cGen2DBundleAttach_Deg2::SetPFixV_x(double aVal){ mLocPFixV_x = aVal;}
void cGen2DBundleAttach_Deg2::SetPFixV_y(double aVal){ mLocPFixV_y = aVal;}



double * cGen2DBundleAttach_Deg2::AdrVarLocFromString(const std::string & aName)
{
   if (aName == "AmplFixV") return & mLocAmplFixV;
   if (aName == "CentrFixV_x") return & mLocCentrFixV_x;
   if (aName == "CentrFixV_y") return & mLocCentrFixV_y;
   if (aName == "FixedV_x") return & mLocFixedV_x;
   if (aName == "FixedV_y") return & mLocFixedV_y;
   if (aName == "PFixV_x") return & mLocPFixV_x;
   if (aName == "PFixV_y") return & mLocPFixV_y;
   return 0;
}


cElCompiledFonc::cAutoAddEntry cGen2DBundleAttach_Deg2::mTheAuto("cGen2DBundleAttach_Deg2",cGen2DBundleAttach_Deg2::Alloc);


cElCompiledFonc *  cGen2DBundleAttach_Deg2::Alloc()
{  return new cGen2DBundleAttach_Deg2();
}

