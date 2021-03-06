#include "include/MMVII_all.h"

#include <algorithm>
#include <tuple>
#include <typeinfo>
#include <forward_list>
#include <unordered_map>
#include <functional>

#include <boost/array.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>

#include <Eigen/Dense>

namespace MMVII
{

class cTestMMV2Obj : public cMemCheck
{
    public :
        virtual ~cTestMMV2Obj()
        {
           TheNbObj--;
        }
        static int NbObj() {return TheNbObj;}
    // protected :
        cTestMMV2Obj()
        {
           TheNbObj++;
        }
    private :
       static int TheNbObj;
};
int cTestMMV2Obj::TheNbObj=0;

void TestCountSharePointer()
{
    {
       std::shared_ptr<cTestMMV2Obj> p0(new cTestMMV2Obj);
       std::shared_ptr<cTestMMV2Obj> p1(new cTestMMV2Obj);

       std::shared_ptr<cTestMMV2Obj> p2 = p0;
       p2 = p1;
       std::cout << "NB OBJ " << cTestMMV2Obj::NbObj() << " =? 2\n";
    }
    std::cout << "NB OBJ " << cTestMMV2Obj::NbObj() << " =? 0\n";
}

    //===============================================

class cFonc1V;

class cDataFonc1V : public  cTestMMV2Obj
{
      public :
           virtual ~cDataFonc1V() {}
           virtual double GetVal(double anX) const = 0;
           virtual cFonc1V Derive() const = 0;
           virtual void Show(std::ostream &) const = 0;

           virtual bool IsCste0() const {return false;}
           virtual bool IsCste1() const {return false;}

      public :
};
// std::ostream & operator << (std::ostream & ofs,const Pt2dUi2  &p);


class  cFonc1V : public  std::shared_ptr<cDataFonc1V> 
{
     public :
         double GetVal(double anX)  {return std::shared_ptr<cDataFonc1V>(*this)->GetVal(anX);}
         cFonc1V Derive() const     {return std::shared_ptr<cDataFonc1V>(*this)->Derive();}

         cFonc1V(double aCste);
         cFonc1V operator + (cFonc1V aF2);
         cFonc1V(cDataFonc1V* aPtr) : std::shared_ptr<cDataFonc1V>(aPtr) {}
};
// static cFonc1V X;

//=============================================

class cDataFonc1V_Cste  : public cDataFonc1V
{
      public :
         cDataFonc1V_Cste(double aCste) : mCste(aCste) {}

         double GetVal(double) const {return mCste;}
         cFonc1V Derive() const {return cFonc1V(0.0);}
         void Show(std::ostream & os) const {os << mCste;}

         bool IsCste0() const {return mCste==0;}
         bool IsCste1() const {return mCste==1;}

      private  :
         double mCste;
};
cFonc1V::cFonc1V(double aCste) :
    std::shared_ptr<cDataFonc1V>(new cDataFonc1V_Cste(aCste))
{
}

//=============================================
class cDataFonc1V_X  : public cDataFonc1V
{
      public :
           cDataFonc1V_X() {std::cout << "CREATE X\n";}
           ~cDataFonc1V_X() {std::cout << "Kill X\n";}

           double GetVal(double aVal) const {return aVal;}
           cFonc1V Derive() const {return cFonc1V(1.0);}
           void Show(std::ostream & os) const {os << "X";}
      private  :
};

static cFonc1V X(new cDataFonc1V_X);



//=============================================
class cDataFonc1V_Som  : public cDataFonc1V
{
     public :
         cDataFonc1V_Som(cFonc1V aF1,cFonc1V aF2) : mF1(aF1) , mF2(aF2) {}

         double  GetVal(double aVal) const {return mF1->GetVal(aVal)+mF2->GetVal(aVal);}
         cFonc1V  Derive() const {return mF1->Derive()+mF2->Derive();}
         void Show(std::ostream & os) const 
         {
               os << "(";
               mF1->Show(os); 
               os << "+";
               mF2->Show(os); 
               os << ")";
         }
     public :
         cFonc1V mF1;
         cFonc1V mF2;
};

cFonc1V cFonc1V::operator + (cFonc1V aF2)
{
   return cFonc1V(new cDataFonc1V_Som(*this,aF2));
}


void  TestSharedPointer()
{
   TestCountSharePointer();

   // new  cFonc1V(3.14);
   // new  cDataFonc1V_Cste(3.14);
   {
       cFonc1V aF = X+3+(X+4);
       std::cout << "F(10) = " << aF.GetVal(10) << " Count= " << cTestMMV2Obj::NbObj() << "\n";
       std::cout << "F'(10) = " << aF.Derive().GetVal(10)  << "\n";
       aF->Show(std::cout) ; std::cout << "\n";
   }
   std::cout  << " Compte final " << cTestMMV2Obj::NbObj() << "\n";
}


/*************************************************************/
/*                                                           */
/*            cAppli_MMVII_TestCpp11                         */
/*                                                           */
/*************************************************************/
template<class Archive>
void serialize(Archive & ar, cPt2dr & aP, const unsigned int version)
{
    ar & aP.x();
    ar & aP.y();
}

void TestBoostSerial()
{
 // create class instance
    std::ofstream ofs("filename");
    const cPt2dr aP(1,2);

    // save data to archive
    {
        boost::archive::text_oarchive oa(ofs);
        // write class instance to archive
        oa << aP;
    	// archive and stream closed when destructors are called
    }

    // ... some time later restore the class instance to its orginal state
    cPt2dr aNewP(0,0);
    {
        // create and open an archive for input
        std::ifstream ifs("filename");
        boost::archive::text_iarchive ia(ifs);
        // read class state from archive
        ia >> aNewP;
        // archive and stream closed when destructors are called
    }
    std::cout  << " AAATestBoostSerial " << aNewP.x() << " " <<  aNewP.y() << "\n";
}

class cAppli_MMVII_TestCpp11 : public cMMVII_Appli
{
     public :
        cAppli_MMVII_TestCpp11(int argc,char** argv) ;
        int Exe();
};

cAppli_MMVII_TestCpp11::cAppli_MMVII_TestCpp11 (int argc,char **argv) :
    cMMVII_Appli
    (
        argc,
        argv,
        DirCur(),
        cArgMMVII_Appli
        (
        )
    )
{
}

// Voir override et  final, pour verifier que le surcharge virtuelle est conforme a nos attentes

// Stong enum 
enum class Cpp11Color { red, blue };   // scoped and strongly typed enum
enum class Cpp11TrafficLight { red, yellow, green };

int  ExternalFonc();

template <class Type> void PrintSzVect(const std::vector<Type> &V);
void PrintSzVectI(const std::vector<int> &V)
{
}

// Constructeur appellant un constructeur pour eviter duplication
// de code
class cCtsrCallCstr
{
    public :
       cCtsrCallCstr(const int & aV) : mV(aV) {}
       cCtsrCallCstr() : cCtsrCallCstr(333) {}
       int mV;
};

// initialisation d'un membre avec une valeur par defaut,
// mais qui peut etre override 
class cWithMembGlobInit
{
    public :
       cWithMembGlobInit() {}
       cWithMembGlobInit(int aV) : mV(aV) {}
       int mV=55;
};
// Assertion statiques verifiees a la compilation
static_assert(1+1==2,"theorme fondamental");
// static_assert(1+1==3,"theorme pas trop utile");

// voir les variadic template, pas sur avoir rencontre le besoin
// 	template<typename Head, typename... Tail>


// auto + -> pour resoudre le probleme du scope dans la valeur de retour
template <class T1,class T2> auto Mul(const T1 & aV1,const T2 & aV2) -> decltype(aV1*aV2) {return aV1*aV2;}

struct sTab3
{
   public :

      sTab3(int x,int y,int z) :
        i {x,y,z}
      {
      }
      int i[3] ;
};

bool fCmpPt(const cPt2dr &aP1,const cPt2dr &aP2){return (aP1.x()+aP1.y()) <  (aP2.x()+aP2.y());}


double Div(double a,double b) {return a/b;}

class cUnikP
{
   public :
      ~cUnikP(){std::cout << "KilledP=" << mMes << "\n";}
      cUnikP(const std::string & aMes) : mMes(aMes) {}
      std::string mMes;
};

std::unique_ptr<cUnikP>  Transfer(const std::string & aMes)
{
      return std::unique_ptr<cUnikP> (new cUnikP(aMes));
}

int cAppli_MMVII_TestCpp11::Exe()
{
   {
       std::string aDir,aFile;
       SplitDirAndFile(aDir,aFile,"./",false);
       SplitDirAndFile(aDir,aFile,mArgv[0],false);
       SplitDirAndFile(aDir,aFile,"/home/ubuntu/Desktop/MMM/micmac/MMVII/bin/",false);
   }
   {
        std::unique_ptr<cUnikP> aP (new cUnikP("T1"));
   }
   std::cout << "END BLOCK T1\n";
   {
        std::unique_ptr<cUnikP> aP2 = Transfer("T2");
        std::cout << " IN  BLOCK T2\n";
   }
   std::cout << "END BLOCK T2\n";

   cPt2dr aP{1,2};
   std::vector<cPt2dr> aVP{{1,2},{3,1},{1,1}};  // Uniform initialization synta

   // Lambda expression fonctionne, mais g++ pas cool sur les erreurs !!!
   
   std::sort(aVP.begin(),aVP.end(), [](const cPt2dr &aP1,const cPt2dr &aP2){return (aP1.x()+aP1.y()) <  (aP2.x()+aP2.y());});
   std::sort(aVP.begin(),aVP.end(), fCmpPt);

   // Local struct
   struct sCmpPt {
       bool operator () (const cPt2dr &aP1,const cPt2dr &aP2){return (aP1.x()+aP1.y()) <  (aP2.x()+aP2.y());}
   };
   std::sort(aVP.begin(),aVP.end(), sCmpPt());



   std::string s = R"(\w\\\w)"; // Raw string , \ is \ !!
   std::string s2 = R"**(\w"()"\\\w)**"; // Raw string  avec "()" etc dedans ... 
   std::cout << "TEST RAW STRING " << s  << "###"  << s2 << "\n";

   auto aTuple = std::make_tuple(1,2.0,"3+2=5");
   std::cout << " T0=> " << std::get<0>(aTuple) << " T2=>" << std::get<2>(aTuple) << " " << "\n";
   
   std::cout << " Type1=> " << typeid(std::get<1>(aTuple)).name()  << "\n";


   char * C= nullptr;  // Un pointeur nul universel, + clean que (char *) 0
   cCtsrCallCstr aT;
   std::cout << "cCtsrCallCstr => " << aT.mV << "\n";
   // PrintSzVect({1,2}); => Pb avec template et initializer , pas sur pb moo ou g++ ?
   PrintSzVectI({1,2});  // Ok sans template
   // Les const expression sont garanties evaluables a la compile
   constexpr auto i = 3+4;
   typedef decltype (1/2.0) mDouble;  // declaration de type a partir d'une expression
   // i++;
   // auto l = constexpr 3+4;
   // l++;
   constexpr  int j = 2*i;
   // const constexpr l = 2;
   // constexpr int k = ExternalFonc(); => pas evaluable a la compile
   // Range
   std::vector<int>  aVI;
   for (auto & it : aVI)
   {
       std::cout << it << "\n";
       it += 2;
   }
   // Range for "enum" values
   for (const auto x : { 2,3,5,7,11 }) std::cout << "Prime ? "  << x << '\n';

   // >> and double range
   std::vector<std::vector<int>>  aVVI;
   for (const auto & it1 : aVVI)
   {
       for (const auto & it2 : it1)
       {
       }
   }


   std::forward_list<int> aFLPrime{2,3,5,7,11,13};
   for (const auto &  it : aFLPrime) std::cout << " " << it ;
   std::cout <<  std::endl;

   std::unordered_map<std::string,int> aUMap{{"Un",1},{"deux",2},{"trois",3},{"Quatre",4}};
   for (const auto &  it : aUMap) std::cout << " " << it.first<<","<<it.second ;
   std::cout <<  std::endl;
   std::cout << "aUMap[Un]=" <<aUMap["Un"] << " aUMap[un]=" << aUMap["un"] << "\n";
   std::cout << " SZUM " << sizeof(aUMap) <<  std::endl;


   // Pas sur supporte par g++ ??? 
   auto Div2 = std::bind(Div,std::placeholders::_1,2.0);
   std::cout <<  " 5/2.0= " << Div2(5.0) << std::endl;
   // auto Div2 = std::bind(Div,std::_1,2.0);
   // auto Div2 = std::bind(Div,std::_1,2.0);
   //auto Div2 = bind(Div,_1,2.0);



   //  revoir les function object, pas trop compris ....
   // voir unique_ptr  (+ ou - comme auto_ptr ?) pour les ptr temporaires a un bloc d'execution

   

   TestSharedPointer();
   TestBoostSerial();
   return EXIT_SUCCESS;

}



tMMVII_UnikPApli Alloc_MMVII_Cpp11(int argc,char ** argv)
{
   return tMMVII_UnikPApli(new cAppli_MMVII_TestCpp11(argc,argv));
}


cSpecMMVII_Appli  TheSpecTestCpp11
(
     "Cpp11",
      Alloc_MMVII_Cpp11,
      "This command execute some test for to check my understanding of C++11",
      "Test",
      "None",
      "Console"
);



};
