// File Automatically generated by eLiSe
#include "general/all.h"
#include "private/all.h"


class cEqAppui_NoDist__GL__PTInc_M2CDCBrown: public cElCompiledFonc
{
   public :

      cEqAppui_NoDist__GL__PTInc_M2CDCBrown();
      void ComputeVal();
      void ComputeValDeriv();
      void ComputeValDerivHessian();
      double * AdrVarLocFromString(const std::string &);
      void SetGL_0_0(double);
      void SetGL_0_1(double);
      void SetGL_0_2(double);
      void SetGL_1_0(double);
      void SetGL_1_1(double);
      void SetGL_1_2(double);
      void SetGL_2_0(double);
      void SetGL_2_1(double);
      void SetGL_2_2(double);
      void SetNDP0_x(double);
      void SetNDP0_y(double);
      void SetNDdx_x(double);
      void SetNDdx_y(double);
      void SetNDdy_x(double);
      void SetNDdy_y(double);
      void SetXIm(double);
      void SetYIm(double);


      static cAutoAddEntry  mTheAuto;
      static cElCompiledFonc *  Alloc();
   private :

      double mLocGL_0_0;
      double mLocGL_0_1;
      double mLocGL_0_2;
      double mLocGL_1_0;
      double mLocGL_1_1;
      double mLocGL_1_2;
      double mLocGL_2_0;
      double mLocGL_2_1;
      double mLocGL_2_2;
      double mLocNDP0_x;
      double mLocNDP0_y;
      double mLocNDdx_x;
      double mLocNDdx_y;
      double mLocNDdy_x;
      double mLocNDdy_y;
      double mLocXIm;
      double mLocYIm;
};