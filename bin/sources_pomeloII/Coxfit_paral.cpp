/*****************************************************************************
 * The file Coxfit.cpp is a modification of the file coxfit2.c, part of the  *
 * survival package for R. These files are originally from Terry Therneau    *
 * (the survival package for S), and were ported to R by Thomas Lumley.      *
 * The survival package is licensed under the GNU GPL. Thus, Coxfit.cpp is   *
 * also licensed under the GNU GPL. I made many changes; mainly, I made many *
 * simplifications for it to use a single covariate and to avoid calling     *
 * several matrix functions, and I also "C++ized" the code.                  *
 * I also added several utility functions.                                   *
 ****************************************************************************/


/****************************************************************************
     Coxfit.cpp: to fit a Cox model with a single covariate.
****************************************************************************/


/***************************************************************************
    begin                : Thu Jul 11 19:21:37 CEST 2002
    copyright            : (C) 2002 - 2006 by Ramón Díaz-Uriarte for the
                           modifications to coxfit2.c.
                           For the original coxfit2.c code, (C) 2000 Mayo 
                           Foundation for Medical Education and Research.
    email                : rdiaz@cnio.es
***************************************************************************/


/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *  This program is distributed in the hope that it will be useful,        *
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of         *
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
 *  GNU General Public License for more details.                           *
 *                                                                         *
 *  You should have received a copy of the GNU General Public License      *
 *  along with this program; if not, write to the Free Software            * 
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,USA *
 *                                                                         *
 **************************************************************************/




#include"Coxfit_paral.h" 
#include<iostream> 
#include<numeric>
#include<fstream> 
#include<valarray> 
#include<cmath>
#include<gsl/gsl_sort_double.h>
//#include"/usr/local/include/gsl/gsl_sort_double.h"

// xx permute_covars should be in multestutil
// covariate centering y all_covariate_centering en multestutil


using namespace std;

void permute_covars(valarray<double> &covariate,
		    valarray<int> &missing,
		    valarray<int> &order_vector, 
		    const int &num_genes,
		    const int &num_subjects) {
/* Order covariates when we are given a vector of the order in which
   they should be. */
// Need to move also the missing data vector since it is associated
// with the covariates

  valarray<double> tmp = covariate;
  valarray<int> tmp_missing = missing;
//  for (int i = 0; i < lenght_data; i++) tmp_covar[i] = covar[i];
  int i = 0;
  for(int j = 0; j < num_genes; j++) {
    for(int k = 0; k < num_subjects; k++) { 
      tmp[(i + k)] = covariate[(i + order_vector[k])];
      tmp_missing[(i + k)] = missing[(i + order_vector[k])];
    }
    i += num_subjects;
  }
  covariate = tmp;
  missing = tmp_missing;
}

void permute_covars_old(double *tmp_covariate, const double *covariate, 
			valarray<int> &order_vector, const int &num_genes,
			const int &num_subjects) {
/* Order covariates when we are given a vector of the order in which
   they should be. */

//  for (int i = 0; i < lenght_data; i++) tmp_covar[i] = covar[i];
  int i = 0;
  for(int j = 0; j < num_genes; j++) {
    for(int k = 0; k < num_subjects; k++) 
      tmp_covariate[(i + k)] = covariate[(i + order_vector[k])];
    i += num_subjects;
  }
}


void all_covariates_centering(std::valarray<double> &covariates, 
			      const std::valarray<int> &missing,
			      const int num_subjects, 
			      const int num_genes) {
  // Deal with missing at the same time as subtract mean
  for(int k = 0; k < num_genes; ++k) {
    double sum_row = 0;
    double mean_row = 0;
    int num_non_missing = 0;
    for(int m = 0; m < num_subjects; ++m) {
      if(!missing[(k * num_subjects) + m]) {
	sum_row += covariates[(k * num_subjects) + m ];
	++num_non_missing;
      }
    }
    mean_row = sum_row/num_non_missing;
    for(int s = 0; s < num_subjects; ++s) 
      covariates[(k * num_subjects) + s] -= mean_row;
  }
}



void sort_for_survival(const int &num_subjects, const int &num_genes, 
		       const int &length_data,
		       std::valarray<double> &survival_time, 
		       std::valarray<int> &censored_status, 
		       std::valarray<double> &covar,
		       std::valarray<int> &missing) {
  /* Before computing the observed statistics, need to sort the 
     data, so that the survival times are in ascending order,
     as required by coxfit2 */

  double *array_survival_time     = new double[num_subjects];
  int *tmp_censored_status      = new int[num_subjects];
  double *tmp_vector            = new double[length_data];
  unsigned int *order_survival  = new unsigned int[num_subjects];

  valarray<int> tmp_missing = missing;
  for (int h = 0; h < num_subjects; ++h) 
    array_survival_time[h] = survival_time[h];

  if((!order_survival) || (!array_survival_time) || 
     (!tmp_vector) || (!tmp_censored_status)) {
    cout << "error allocation failure in sort_for_survival" << endl;
    exit(1);
  }
  gsl_sort_index(order_survival, array_survival_time, 1, num_subjects);
  // recall gsl_sort_index leaves survival_time untouched, so need to sort it.

  for (int m = 0; m < num_subjects; m++) {
    tmp_censored_status[m] = censored_status[m];
  }
  for (int m = 0; m < num_subjects; m++) {
    survival_time[m] = array_survival_time[order_survival[m]];
    censored_status[m] = tmp_censored_status[order_survival[m]];
  }
  

  for (int m = 0; m < length_data; m++) tmp_vector[m] = covar[m];
  int i = 0;
  for(int j = 0; j < num_genes; j++) {
    for(int k = 0; k < num_subjects; k++) {
      covar[(i + k)] = tmp_vector[(i + order_survival[k])];
      missing[(i + k)] = tmp_missing[(i + order_survival[k])];
    }  
    i += num_subjects;
  }

  delete [] tmp_vector;
  delete [] tmp_censored_status;
  delete [] array_survival_time;
  delete [] order_survival;
}


// void coxfit2(int   &maxiter,   const int   &nusedx,    
// 	     const double *time,      const int   *status,  const double *covar, 
// 	     double &beta, double &imat, double *loglik,  int   &flag, 
// 	     const double &eps, double &u); 

void compute_cox_statistic(valarray<double> &test_statistic,
			   const double *time, const int *status, 
			   const double  *covar,
			   const int &num_genes, const int &num_subjects,
			   const int &maxiter, const double &eps,
			   const valarray<int> &MissingArray) { 
  int i = 0;

  for(int j = 0; j < num_genes; j++) {
    // We would really only need to initialize beta= 0 
    //  and maixer_routine = maxiter
    // in this loop.
  double beta = 0;
  double imat2 = 0;
  double loglik[2] = {0, 0};
  double u = 0;
  int success_flag = 1;
  int maxiter_routine = maxiter; //to allow coxfit to modify, 
                           // but always pass the righ value.
  // yyxx: need to work on this.

  // Missing values part

//  cout << "     Missing values part " << endl; //zz
  int num_non_missing = num_subjects - MissingArray[slice(i,num_subjects, 1)].sum();
  double *tmp_data            = new double[num_non_missing];
  double *tmp_survival_time   = new double[num_non_missing];
  int    *tmp_censored_status = new int[num_non_missing];

    // Deal with missing: assign values to the temporaries
    // only if non-missing.
    // There are ways of doing this were I don't need to repeat
    // this step at each iteration, but I would need to change
    // the loops. We'll see if it is needed when profiling.
    // Do it as follows:
//       a vector with length of each "row" without missing
//       a vector with position of missing
//       the loop in jumps not of num_HS, but of number of non-missing per row.
//       eliminate the value of class_label corresponding to the missing
//       position.
//       the first tow not necessary in a per loop basis.
    int n = 0;
    for(int m = 0; m < num_subjects; m++) {
      if(!MissingArray[i + m]) {
         tmp_data[n] = covar[i + m];
         tmp_survival_time[n] = time[m];
         tmp_censored_status[n] = status[m];
         ++n;
      }
    }


//    cout << "      Right before calling coxfit2 " << endl; //zz
    coxfit2(maxiter_routine, num_non_missing, tmp_survival_time, 
	    tmp_censored_status, tmp_data, beta, imat2, loglik, 
	    success_flag, eps, u);
    test_statistic[j] = beta/sqrt(imat2);
//     if (success_flag != 1) {
// //       log_out << "\n WARNING (1): Non-convergence in gene " << j 
// // 	      <<" with flag " << success_flag << " iterations " 
// // 	      << maxiter_routine <<"\n; beta = " << beta 
// // 	      <<" se(beta) = " <<sqrt(imat2) << "loglik " 
// // 	      << loglik[0] <<" " << loglik[1]<< endl;
// //       log_out << "\n Covar is " << j << endl;
// //       // the output can be directyl read into R to check
// //       log_out <<"c(";
// //       for(int m = 0; m <(num_non_missing-1) ; m++) log_out <<covar[i+m] << ", ";
// //       log_out << covar[i + num_non_missing - 1];
// //       log_out <<") \n";
// 
//       log_out << "\n Survival time is " << j << endl;
//       // the output can be directyl read into R to check
//       log_out <<"c(";
//       for(int m = 0; m < (num_non_missing -1) ; m++) log_out <<time[m] << ", ";
//       log_out << time[num_non_missing - 1];
//       log_out <<") \n";
// 
//       log_out << "\n Censored status is " << j << endl;
//       // the output can be directyl read into R to check
//       log_out <<"c(";
//       for(int m = 0; m <(num_non_missing-1) ; m++) log_out << status[m] << ", ";
//       log_out << status[num_non_missing - 1];
//       log_out <<") \n";
//       //cout << "CONVERGENCE PROBLEM FOR THE ABOVE STUFF AT GENE " << j << endl;
//     }
//    if((abs(u * imat2) > eps) && (abs(u * imat2) > (sqrt(eps) *abs(beta)))) {
//       log_out << "\n \n WARNING (2): Loglik converged before the covariate; "
// 	      <<" beta may be infinite in gene " 
// 	      << j <<" with flag " << success_flag << " iterations " 
// 	      << maxiter_routine 
// 	      << "\n; beta = " << beta <<" se(beta) = " << sqrt(imat2) 
// 	      << " loglik "  << loglik[0] <<" " << loglik[1] << endl;
//       log_out << "\n Covar is " << j << endl;
//       // the output can be directyl read into R to check
//       log_out <<"c(";
//       for(int m = 0; m < (num_non_missing -1) ; m++) 
// 	log_out << covar[i+m] << ", ";
//       log_out << covar[i + num_non_missing - 1];
//       log_out <<") \n";
// 
//       log_out << "\n Survival time is " << j << endl;
//       // the output can be directyl read into R to check
//       log_out <<"c(";
//       for(int m = 0; m < (num_non_missing -1) ; m++) 
// 	log_out << time[m] << ", ";
//       log_out << time[num_non_missing - 1];
//       log_out <<") \n";
// 
//       log_out << "\n Censored status is " << j << endl;
//       // the output can be directyl read into R to check
//       log_out <<"c(";
//       for(int m = 0; m <(num_non_missing-1) ; m++) log_out <<status[m] << ", ";
//       log_out << status[num_non_missing - 1];
//       log_out <<") \n";
      //cout <<"LOGLIK CONVERGED BEFORE COVARIATE; BETA MAY BE INFINITE AT GENE" 
	//   << j << endl;
//    }
    i += num_subjects;
    delete[] tmp_data;
    delete[] tmp_survival_time;
    delete[] tmp_censored_status;
  }
}






/**********************************************************************
***********************************************************************

                           coxfit2 function

***********************************************************************
**********************************************************************/


/* This function is based on coxfit2.c, from the survival package for R,
written by T. Therneau. I have:
    - Simplified it for just one covariate; this allows not to use
      cholesky2, chsolve2 and chinv2, but rather simple division.
    - Eliminated weights, strata, and offset.
    - "C++ized" some of the code (new and delete, casts, call by reference, 
       etc).

The function REQUIRES:
    - The survival times to be sorted by ascending order (as in coxfit2.c).
    - It is convenient to have the covariates centered. This is done now
    outside this function (to speed up use of this function in 
    permutation tests).
    The function for centering is covariate_centering (see above).

For completenes, I leave the original description of the function below.
Beware that some of the comments no longer apply.
Beware that indentation is not always consistent because I have deleted
and commented out a lot of the original code.

*/


/*  SCCS @(#)coxfit2.c	5.1 08/30/98*/
/*
** here is a cox regression program, written in c
**     uses Efron's approximation for ties
**  the input parameters are
**
**       maxiter      :number of iterations
**       nused        :number of people
**       nvar         :number of covariates
**       time(n)      :time of event or censoring for person i
**       status(n)    :status for the ith person    1=dead , 0=censored
**       covar(nv,n)  :covariates for person i.
**                        Note that S sends this in column major order.
**       strata(n)    :marks the strata.  Will be 1 if this person is the
**                       last one in a strata.  If there are no strata, the
**                       vector can be identically zero, since the nth person's
**                       value is always assumed to be = to 1.
**       offset(n)    :offset for the linear predictor
**       weights(n)   :case weights
**       eps          :tolerance for convergence.  Iteration continues until
**                       the percent change in loglikelihood is <= eps.
**       chol_tol     : tolerance for the Cholesky decompostion
**       sctest       : on input contains the method 0=Breslow, 1=Efron
**
**  returned parameters
**       means(nv)    : vector of column means of X
**       beta(nv)     :the vector of answers (at start contains initial est)
**       u(nv)        :score vector
**       imat(nv,nv)  :the variance matrix at beta=final, also a ragged array
**                      if flag<0, imat is undefined upon return
**       loglik(2)    :loglik at beta=initial values, at beta=final
**       sctest       :the score test at beta=initial
**       flag         :success flag  1000  did not converge
**                                   1 to nvar: rank of the solution
**       maxiter      :actual number of iterations used
**
**  work arrays
**       mark(n)
**       wtave(n)
**       a(nvar), a2(nvar)
**       cmat(nvar,nvar)       ragged array
**       cmat2(nvar,nvar)
**       newbeta(nvar)         always contains the "next iteration"
**
**  the work arrays are passed as a single
**    vector of storage, and then broken out.
**
**  calls functions:  cholesky2, chsolve2, chinv2
**
**  the data must be sorted by ascending time within strata
*/
void coxfit2(int   &maxiter,   const int   &nusedx,    
	     const double *time,      const int   *status, const double *covar, 
	     double &beta, double &imat, double *loglik,  int   &flag, 
	     const double &eps, double &u) 
{
    register int i,j,k, person;
    int iter;
//    int nused, nvar;
    int nused;
    double a, newbeta;
    double a2;
    double denom = 0;
    double zbeta, risk; 
    double  temp, temp2;
    double  ndead;
    double  newlk = 0;
    double  d2, efron_wt;
    int  halving;    
    double method = 1;

    nused = nusedx;
//    nvar  = nvarx;


//    double means = 0;
    //double u = 0;

//    double *covar = new double[nused];
//    for (int i = 0; i < nused; i++) covar[i] = covar2[i]; 
//    double imat;
    double cmat;
    double cmat2;


    double *mark = new double[nused];
    double *wtave = new double[nused]; 
 
    /*
    **   Mark(i) contains the number of tied deaths at this point,
    **    for the first person of several tied times. It is zero for
    **    the second and etc of a group of tied times.
    **   Wtave contains the average weight for the deaths
    */
    temp=0;
    j=0;
    for (i=nused-1; i>0; i--) {
//	if ((time[i]==time[i-1]) & (strata[i-1] != 1)) {
	if (time[i] == time[i-1]) {
	    j += status[i];
	    temp += status[i];
	    mark[i]=0;
	    }
	else  {
	    mark[i] = j + status[i];
	    if (mark[i] >0) wtave[i]= (temp+ status[i])/ mark[i];
	    temp=0; j=0;
	    }
	}
    mark[0]  = j + status[0];
    if (mark[0]>0) wtave[0] = (temp +status[0])/ mark[0];

    /*
    ** Subtract the mean from each covar, as this makes the regression
    **  much more stable
    */

    /*  xx: starting here, go over the code and get rid of the iterations
	over variables, as only one. */
    //double temp = 0;
//    double means = 0;

//  	temp=0;
//  	for (person=0; person<nused; person++) temp += covar[person];
//  	temp /= nused;
//  	means = temp;
//  	for (person=0; person<nused; person++) covar[person] -=temp;
	//}

    /*
    ** do the initial iteration step
    */
//    strata[nused-1] =1;
    loglik[1] =0;
    u = 0; // this is new xxx
    a = a2 = 0; // this is new xxx
    imat =0;
    efron_wt =0;
    denom = 0;
    cmat = cmat2 = 0;


  for (person=nused-1; person>=0; person--) {
// 	if (strata[person] == 1) {
// 	    denom = 0;
// 		    cmat = 0;
// 		    cmat2= 0;
// 	}

      zbeta = 0;    /* form the term beta*z   (vector mult) */
      zbeta += beta*covar[person];
      risk = exp(zbeta);
      denom += risk;
      efron_wt += status[person] * risk;  /*sum(denom) for tied deaths*/

    a += risk*covar[person];
    cmat += risk*covar[person]*covar[person];

    if (status[person]==1) {
      loglik[1] += zbeta;
      u += covar[person];
      a2 +=  risk*covar[person];
      cmat2 += risk*covar[person]*covar[person];

    }
	if (mark[person] >0) {  /* once per unique death time */
	    /*
	    ** Trick: when 'method==0' then temp=0, giving Breslow's method
	    */
	    ndead = mark[person];
	    for (k=0; k<ndead; k++) {
		temp = static_cast<double>(k) * method / ndead;
		d2= denom - temp*efron_wt;
		loglik[1] -= wtave[person] * log(d2);

		    temp2 = (a - temp*a2)/ d2;
		    u -= wtave[person] * temp2;

			imat +=  wtave[person]*(
				 (cmat - temp*cmat2) /d2 -
					  temp2*(a-temp*a2)/d2);

		}
	    efron_wt =0;
	    a2 = 0;
		  cmat2=0;

	}
	}   /* end  of accumulation loop */

    loglik[0] = loglik[1];   /* save the loglik for iteration zero  */


    /* am I done?
    **   update the betas and test for convergence
    */
    /*use 'a' as a temp to save u0, for the score test*/
    //for (i=0; i<nvar; i++) 
	a = u;
    //*flag= cholesky2(imat, nvar, *tol_chol);
    //chsolve2(imat,nvar,a);        a replaced by  a *inverse(i) 
    flag = 1; // a capón, pero con nvar = 1... xx: check if not PSD.
    if (imat == 0) std::cout <<"\n ERROR division by 0 in *a /= imat \n";
    a /= imat; //xx: ojo con divisiones por 0...
    
    //*sctest=0;
    //*sctest +=  u*a;

    /*
    **  Never, never complain about convergence on the first step.  That way,
    **  if someone HAS to they can force one iter at a time.
    */
//    for (i=0; i<nvar; i++) {
	newbeta = beta + a;
//	}
    if (maxiter==0) {
//	chinv2(imat,nvar); no tengo claro que sea el inverso o el inverso de sqrt.
      imat = 1/imat;
	//for (i=1; i<nvar; i++)
	   // for (j=0; j<i; j++)  imat = imat;
      cout <<"\n ERROR We should never be here, since maxiter always > 0 \n";
	return;   /* and we leave the old beta in peace */
	}

    /*
    ** here is the main loop
    */
    halving =0 ;             /* =1 when in the midst of "step halving" */
    for (iter=1; iter <= maxiter; iter++) {
	newlk =0;
    u =0;
    imat =0;
	
    // Following lines used to be inside strata loop
    efron_wt =0;
    denom = 0;
    a = 0;
    a2=0 ;
    cmat = 0;
    cmat2= 0;

    
	for (person=nused-1; person>=0; person--) {
// 	    if (strata[person] == 1) {
// 		efron_wt =0;
// 		denom = 0;
// 		a = 0;
// 		a2=0 ;
// 		cmat = 0;
// 		cmat2= 0;
// 		}

    zbeta = 0;
    zbeta += newbeta*covar[person];
    risk = exp(zbeta);

    denom += risk;
    efron_wt += status[person] * risk;  /* sum(denom) for tied deaths*/
    
    
    a += risk*covar[person];
    
    cmat += risk*covar[person]*covar[person];
	
    
    if (status[person]==1) {
      newlk += zbeta;
      u += covar[person];
      a2 +=  risk*covar[person];
      cmat2 += risk*covar[person]*covar[person];
    }

    if (mark[person] >0) {  /* once per unique death time */
      for (k=0; k<mark[person]; k++) {
	temp = (double)k* method /mark[person];
	d2= denom - temp*efron_wt;
	newlk -= wtave[person] *log(d2);
	temp2 = (a - temp*a2)/ d2;
	u -= wtave[person] *temp2;
	imat +=  wtave[person] * ((cmat - temp*cmat2) /d2 - temp2*(a-temp*a2)/d2);
      }
      efron_wt =0;
      a2=0;
      cmat2 = 0;
    }
	}   /* end  of accumulation loop  */

	/* am I done?
	**   update the betas and test for convergence
	*/
	//*flag = cholesky2(imat, nvar, *tol_chol);
	flag = 1;

	if (abs(1-(loglik[1]/newlk)) <= eps) { /* all done */
	    loglik[1] = newlk;
	    //chinv2(imat, nvar);    invert info matrix
	    imat = 1/imat;
	    //for (i=1; i<nvar; i++)
	    //	for (j=0; j<i; j++)  imat = imat;
	    //for (i=0; i<nvar; i++)
	      beta = newbeta;
	    if (halving==1) flag= 1000; /*didn't converge after all */
	    		if(halving == 1) { //xx:debugging:
// 			  cout <<"\n halving = 1, flag = 1000, imat " << imat 
// 			       << " beta " << beta 
// 			       << "\n newlk " << newlk << " loglik[1] " 
// 			       << loglik[1] << " loglik[0] " << loglik[0] 
// 			       << endl;
// 			  cout <<"\n Survival time :";
// 			  for(int kk = 0; kk < nusedx; kk++) 
// 			    cout << time[kk] <<" ";
// 			  cout <<"\n Censored status :";
// 			  for(int kk = 0; kk < nusedx; kk++) 
// 			    cout << status[kk] <<" ";
// 			  cout <<"\n Covar :";
// 			  for(int kk = 0; kk < nusedx; kk++) 
// 			    cout << covar[kk] <<" ";
// 	  		  cout << endl;
			}
			   
	    maxiter = iter;
//	        delete [] covar;
		delete [] mark;
		delete [] wtave;
		  
	    return;
	    }

	if (iter == maxiter) break;  /*skip the step halving and etc */

	if (newlk < loglik[1])   {    /*it is not converging ! */
		halving =1;
//		for (i=0; i<nvar; i++)
		    newbeta = (newbeta + beta) /2; /*half of old increment */
		}
	    else {
		halving=0;
		loglik[1] = newlk;
		//chsolve2(imat,nvar,u);
		if (imat == 0) std::cout <<"\n ERROR division by 0 in u /= imat \n";
		u /= imat; //xx: ojo con divisiones por 0...
		j=0;
	    beta = newbeta;
	    newbeta = newbeta +  u;

		}
	}   /* return for another iteration */

//xx:debugging:
 // cout <<"\n REACHED MAXITER, flag = 1000, imat " << imat << " beta " 
//       << beta << " newbeta " << newbeta
//       << "\n newlk " << newlk << " loglik[1] " << loglik[1] 
//       << " loglik[0] " << loglik[0] << endl;
//  cout <<"\n Survival time :";
//  for(int kk = 0; kk < nusedx; kk++) cout << time[kk] <<" ";
//  cout <<"\n Censored status :";
//  for(int kk = 0; kk < nusedx; kk++) cout << status[kk] <<" ";
//  cout <<"\n Covar :";
//  for(int kk = 0; kk < nusedx; kk++) cout << covar[kk] <<" ";
//  cout << endl;
    loglik[1] = newlk;
    imat = 1/imat;
	beta = newbeta;
    flag= 1000;

//    delete [] covar;
    delete [] mark;
    delete [] wtave;

    return;

}

