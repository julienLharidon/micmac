// File Automatically generated by eLiSe
#include "StdAfx.h"
#include "cREgDistVal_Four11x2.h"


cREgDistVal_Four11x2::cREgDistVal_Four11x2():
    cElCompiledFonc(2)
{
   AddIntRef (cIncIntervale("Intr",0,16));
   Close(false);
}



void cREgDistVal_Four11x2::ComputeVal()
{
   double tmp0_ = mLocRegDistValP1_x - mLocFour11x2_State_1_0;
   double tmp1_ = (tmp0_) / mLocFour11x2_State_0_0;
   double tmp2_ = mLocRegDistValP1_y - mLocFour11x2_State_2_0;
   double tmp3_ = (tmp2_) / mLocFour11x2_State_0_0;
   double tmp4_ = mCompCoord[9];
   double tmp5_ = tmp1_ - tmp4_;
   double tmp6_ = mCompCoord[10];
   double tmp7_ = tmp3_ - tmp6_;
   double tmp8_ = (tmp5_) * (tmp5_);
   double tmp9_ = (tmp7_) * (tmp7_);
   double tmp10_ = tmp8_ + tmp9_;
   double tmp11_ = (tmp10_) * (tmp10_);
   double tmp12_ = tmp11_ * (tmp10_);
   double tmp13_ = tmp12_ * (tmp10_);
   double tmp14_ = mCompCoord[3];
   double tmp15_ = mCompCoord[4];
   double tmp16_ = mCompCoord[5];
   double tmp17_ = (tmp1_) * (tmp3_);
   double tmp18_ = mCompCoord[6];
   double tmp19_ = (tmp3_) * (tmp3_);
   double tmp20_ = (tmp1_) * (tmp1_);
   double tmp21_ = mCompCoord[11];
   double tmp22_ = tmp21_ * (tmp10_);
   double tmp23_ = mCompCoord[12];
   double tmp24_ = tmp23_ * tmp11_;
   double tmp25_ = tmp22_ + tmp24_;
   double tmp26_ = mCompCoord[13];
   double tmp27_ = tmp26_ * tmp12_;
   double tmp28_ = tmp25_ + tmp27_;
   double tmp29_ = mCompCoord[14];
   double tmp30_ = tmp29_ * tmp13_;
   double tmp31_ = tmp28_ + tmp30_;
   double tmp32_ = mCompCoord[15];
   double tmp33_ = tmp13_ * (tmp10_);
   double tmp34_ = tmp32_ * tmp33_;
   double tmp35_ = tmp31_ + tmp34_;

  mVal[0] = (mLocFour11x2_State_1_0 + (((1 + tmp14_) * (tmp1_) + tmp15_ * (tmp3_)) - tmp16_ * 2 * tmp20_ + tmp18_ * tmp17_ + mCompCoord[7] * tmp19_ + (tmp5_) * (tmp35_)) * mLocFour11x2_State_0_0) - mLocRegDistKnownVal_x;

  mVal[1] = (mLocFour11x2_State_2_0 + (((1 - tmp14_) * (tmp3_) + tmp15_ * (tmp1_) + tmp16_ * tmp17_) - tmp18_ * 2 * tmp19_ + mCompCoord[8] * tmp20_ + (tmp7_) * (tmp35_)) * mLocFour11x2_State_0_0) - mLocRegDistKnownVal_y;

}


void cREgDistVal_Four11x2::ComputeValDeriv()
{
   double tmp0_ = mLocRegDistValP1_x - mLocFour11x2_State_1_0;
   double tmp1_ = (tmp0_) / mLocFour11x2_State_0_0;
   double tmp2_ = mLocRegDistValP1_y - mLocFour11x2_State_2_0;
   double tmp3_ = (tmp2_) / mLocFour11x2_State_0_0;
   double tmp4_ = mCompCoord[9];
   double tmp5_ = tmp1_ - tmp4_;
   double tmp6_ = mCompCoord[10];
   double tmp7_ = tmp3_ - tmp6_;
   double tmp8_ = (tmp5_) * (tmp5_);
   double tmp9_ = (tmp7_) * (tmp7_);
   double tmp10_ = tmp8_ + tmp9_;
   double tmp11_ = (tmp10_) * (tmp10_);
   double tmp12_ = tmp11_ * (tmp10_);
   double tmp13_ = tmp12_ * (tmp10_);
   double tmp14_ = (tmp1_) * (tmp1_);
   double tmp15_ = (tmp1_) * (tmp3_);
   double tmp16_ = (tmp3_) * (tmp3_);
   double tmp17_ = mCompCoord[11];
   double tmp18_ = tmp17_ * (tmp10_);
   double tmp19_ = mCompCoord[12];
   double tmp20_ = tmp19_ * tmp11_;
   double tmp21_ = tmp18_ + tmp20_;
   double tmp22_ = mCompCoord[13];
   double tmp23_ = tmp22_ * tmp12_;
   double tmp24_ = tmp21_ + tmp23_;
   double tmp25_ = mCompCoord[14];
   double tmp26_ = tmp25_ * tmp13_;
   double tmp27_ = tmp24_ + tmp26_;
   double tmp28_ = mCompCoord[15];
   double tmp29_ = tmp13_ * (tmp10_);
   double tmp30_ = tmp28_ * tmp29_;
   double tmp31_ = tmp27_ + tmp30_;
   double tmp32_ = -(1);
   double tmp33_ = tmp32_ * (tmp5_);
   double tmp34_ = tmp33_ + tmp33_;
   double tmp35_ = (tmp34_) * (tmp10_);
   double tmp36_ = tmp35_ + tmp35_;
   double tmp37_ = (tmp36_) * (tmp10_);
   double tmp38_ = (tmp34_) * tmp11_;
   double tmp39_ = tmp37_ + tmp38_;
   double tmp40_ = (tmp39_) * (tmp10_);
   double tmp41_ = (tmp34_) * tmp12_;
   double tmp42_ = tmp40_ + tmp41_;
   double tmp43_ = tmp32_ * (tmp7_);
   double tmp44_ = tmp43_ + tmp43_;
   double tmp45_ = (tmp44_) * (tmp10_);
   double tmp46_ = tmp45_ + tmp45_;
   double tmp47_ = (tmp46_) * (tmp10_);
   double tmp48_ = (tmp44_) * tmp11_;
   double tmp49_ = tmp47_ + tmp48_;
   double tmp50_ = (tmp49_) * (tmp10_);
   double tmp51_ = (tmp44_) * tmp12_;
   double tmp52_ = tmp50_ + tmp51_;
   double tmp53_ = mCompCoord[3];
   double tmp54_ = mCompCoord[4];
   double tmp55_ = mCompCoord[5];
   double tmp56_ = mCompCoord[6];
   double tmp57_ = (tmp1_) * mLocFour11x2_State_0_0;
   double tmp58_ = tmp15_ * mLocFour11x2_State_0_0;
   double tmp59_ = (tmp34_) * tmp17_;
   double tmp60_ = (tmp36_) * tmp19_;
   double tmp61_ = tmp59_ + tmp60_;
   double tmp62_ = (tmp39_) * tmp22_;
   double tmp63_ = tmp61_ + tmp62_;
   double tmp64_ = (tmp42_) * tmp25_;
   double tmp65_ = tmp63_ + tmp64_;
   double tmp66_ = (tmp42_) * (tmp10_);
   double tmp67_ = (tmp34_) * tmp13_;
   double tmp68_ = tmp66_ + tmp67_;
   double tmp69_ = (tmp68_) * tmp28_;
   double tmp70_ = tmp65_ + tmp69_;
   double tmp71_ = tmp32_ * (tmp31_);
   double tmp72_ = (tmp44_) * tmp17_;
   double tmp73_ = (tmp46_) * tmp19_;
   double tmp74_ = tmp72_ + tmp73_;
   double tmp75_ = (tmp49_) * tmp22_;
   double tmp76_ = tmp74_ + tmp75_;
   double tmp77_ = (tmp52_) * tmp25_;
   double tmp78_ = tmp76_ + tmp77_;
   double tmp79_ = (tmp52_) * (tmp10_);
   double tmp80_ = (tmp44_) * tmp13_;
   double tmp81_ = tmp79_ + tmp80_;
   double tmp82_ = (tmp81_) * tmp28_;
   double tmp83_ = tmp78_ + tmp82_;

  mVal[0] = (mLocFour11x2_State_1_0 + (((1 + tmp53_) * (tmp1_) + tmp54_ * (tmp3_)) - tmp55_ * 2 * tmp14_ + tmp56_ * tmp15_ + mCompCoord[7] * tmp16_ + (tmp5_) * (tmp31_)) * mLocFour11x2_State_0_0) - mLocRegDistKnownVal_x;

  mCompDer[0][0] = 0;
  mCompDer[0][1] = 0;
  mCompDer[0][2] = 0;
  mCompDer[0][3] = tmp57_;
  mCompDer[0][4] = (tmp3_) * mLocFour11x2_State_0_0;
  mCompDer[0][5] = -(2 * tmp14_) * mLocFour11x2_State_0_0;
  mCompDer[0][6] = tmp58_;
  mCompDer[0][7] = tmp16_ * mLocFour11x2_State_0_0;
  mCompDer[0][8] = 0;
  mCompDer[0][9] = (tmp71_ + (tmp70_) * (tmp5_)) * mLocFour11x2_State_0_0;
  mCompDer[0][10] = (tmp83_) * (tmp5_) * mLocFour11x2_State_0_0;
  mCompDer[0][11] = (tmp10_) * (tmp5_) * mLocFour11x2_State_0_0;
  mCompDer[0][12] = tmp11_ * (tmp5_) * mLocFour11x2_State_0_0;
  mCompDer[0][13] = tmp12_ * (tmp5_) * mLocFour11x2_State_0_0;
  mCompDer[0][14] = tmp13_ * (tmp5_) * mLocFour11x2_State_0_0;
  mCompDer[0][15] = tmp29_ * (tmp5_) * mLocFour11x2_State_0_0;
  mVal[1] = (mLocFour11x2_State_2_0 + (((1 - tmp53_) * (tmp3_) + tmp54_ * (tmp1_) + tmp55_ * tmp15_) - tmp56_ * 2 * tmp16_ + mCompCoord[8] * tmp14_ + (tmp7_) * (tmp31_)) * mLocFour11x2_State_0_0) - mLocRegDistKnownVal_y;

  mCompDer[1][0] = 0;
  mCompDer[1][1] = 0;
  mCompDer[1][2] = 0;
  mCompDer[1][3] = tmp32_ * (tmp3_) * mLocFour11x2_State_0_0;
  mCompDer[1][4] = tmp57_;
  mCompDer[1][5] = tmp58_;
  mCompDer[1][6] = -(2 * tmp16_) * mLocFour11x2_State_0_0;
  mCompDer[1][7] = 0;
  mCompDer[1][8] = tmp14_ * mLocFour11x2_State_0_0;
  mCompDer[1][9] = (tmp70_) * (tmp7_) * mLocFour11x2_State_0_0;
  mCompDer[1][10] = (tmp71_ + (tmp83_) * (tmp7_)) * mLocFour11x2_State_0_0;
  mCompDer[1][11] = (tmp10_) * (tmp7_) * mLocFour11x2_State_0_0;
  mCompDer[1][12] = tmp11_ * (tmp7_) * mLocFour11x2_State_0_0;
  mCompDer[1][13] = tmp12_ * (tmp7_) * mLocFour11x2_State_0_0;
  mCompDer[1][14] = tmp13_ * (tmp7_) * mLocFour11x2_State_0_0;
  mCompDer[1][15] = tmp29_ * (tmp7_) * mLocFour11x2_State_0_0;
}


void cREgDistVal_Four11x2::ComputeValDerivHessian()
{
  ELISE_ASSERT(false,"Foncteur cREgDistVal_Four11x2 Has no Der Sec");
}

void cREgDistVal_Four11x2::SetFour11x2_State_0_0(double aVal){ mLocFour11x2_State_0_0 = aVal;}
void cREgDistVal_Four11x2::SetFour11x2_State_1_0(double aVal){ mLocFour11x2_State_1_0 = aVal;}
void cREgDistVal_Four11x2::SetFour11x2_State_2_0(double aVal){ mLocFour11x2_State_2_0 = aVal;}
void cREgDistVal_Four11x2::SetRegDistKnownVal_x(double aVal){ mLocRegDistKnownVal_x = aVal;}
void cREgDistVal_Four11x2::SetRegDistKnownVal_y(double aVal){ mLocRegDistKnownVal_y = aVal;}
void cREgDistVal_Four11x2::SetRegDistValP1_x(double aVal){ mLocRegDistValP1_x = aVal;}
void cREgDistVal_Four11x2::SetRegDistValP1_y(double aVal){ mLocRegDistValP1_y = aVal;}



double * cREgDistVal_Four11x2::AdrVarLocFromString(const std::string & aName)
{
   if (aName == "Four11x2_State_0_0") return & mLocFour11x2_State_0_0;
   if (aName == "Four11x2_State_1_0") return & mLocFour11x2_State_1_0;
   if (aName == "Four11x2_State_2_0") return & mLocFour11x2_State_2_0;
   if (aName == "RegDistKnownVal_x") return & mLocRegDistKnownVal_x;
   if (aName == "RegDistKnownVal_y") return & mLocRegDistKnownVal_y;
   if (aName == "RegDistValP1_x") return & mLocRegDistValP1_x;
   if (aName == "RegDistValP1_y") return & mLocRegDistValP1_y;
   return 0;
}


cElCompiledFonc::cAutoAddEntry cREgDistVal_Four11x2::mTheAuto("cREgDistVal_Four11x2",cREgDistVal_Four11x2::Alloc);


cElCompiledFonc *  cREgDistVal_Four11x2::Alloc()
{  return new cREgDistVal_Four11x2();
}


