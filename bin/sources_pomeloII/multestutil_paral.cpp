/***************************************************************************
    multestutil_paral.cpp: utlities et al. for multiple testing
***************************************************************************/ 
/***************************************************************************
    begin                : Thu Jul 11 19:21:37 CEST 2002
    copyright            : (C) 2002, 2003, 2004 by Ramón Díaz-Uriarte,
                               2005, 2006  by Edward R. Morrissey and
                                           Ramon Diaz-Uriarte
    email                : rdiaz02@gmail.com, ermorrissey@cnio.es
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

#include"multestutil_paral.h"
#include"readMissing.h" //need to know about input_data_struct
#include"Coxfit_paral.h"  

extern "C" {
  #include"fisher2.h" //The C code, modified from R, for Fisher's test.
}

#include<iostream>
#include<cstdlib>
#include<algorithm>
#include<numeric>
#include<vector>
#include<fstream>
#include<string>
#include<valarray>
#include<ctime> //to seed the random number generators, if no seed is explicitly given
#include<cmath>

// Change the following, and use R.
#include<gsl/gsl_math.h>
#include<gsl/gsl_rng.h>
#include<gsl/gsl_randist.h>
#include<gsl/gsl_statistics_double.h> //quitar cuando quitemos test t
#include<gsl/gsl_sort_double.h>
#include<gsl/gsl_combination.h>
#include<gsl/gsl_sf_gamma.h> //To obtain choose(m,k);

//#define PR(x) cout <<"\n" <<  #x << " = " << x << endl;
#define PR(x)

// Here are the multiple testing routines that are used by
// most of the programs.
// Also included are the random number generation  and
// random shuffling calls.


using namespace std;



// I have added a fuzzy factor, as suggested in Westfall & Young, 1993,
// p. 166. I add it in the following functions:
   // a) increase_unadjusted_p_value_counter
   // b) increase_adjusted_p_value_counter
// for now, this is the hack:
const extern double fuzz_factor = 1e-14;
//const extern double fuzz_factor = -1e-14;


void compute_test_statistic(unsigned int       aux_length_data,
			    unsigned int       aux_num_columns,
			    unsigned int       aux_num_rows,
			    valarray<int>      val_missing,
			    valarray<double>   val_covariates,
			    valarray<double>   val_columns,
			    valarray<int>      val_columns_int,
			    valarray<int>      val_censored_status,
			    valarray<double>   &test_statistic,
			    string             type_statistic,
			    const int          &number_of_run) {

   if(type_statistic == "t") {
     //valarray<int> class_labels(datos.num_columns);
     //for (unsigned int m = 0; m < datos.num_columns; ++m) class_labels[m] =static_cast<int>(datos.columns[m]);
      compute_t_test(test_statistic, val_covariates, val_columns_int,
 		    aux_num_rows, aux_num_columns,
 		    val_missing, number_of_run);
   }
   else if(type_statistic == "Anova") {
    // valarray<int> class_labels(datos.num_columns);
    // for (unsigned int m = 0; m < datos.num_columns; ++m) class_labels[m] =static_cast<int>(datos.columns[m]);
     compute_F_test(test_statistic, val_covariates, val_columns_int,
 		    aux_num_rows, aux_num_columns,
 		    val_missing, number_of_run);
   }
   else if(type_statistic == "Regres") {
     compute_regression_test(test_statistic, val_covariates, val_columns,
			     aux_num_rows, aux_num_columns,
			     val_missing, number_of_run); 
   }    
   else if(type_statistic == "FisherIxJ") {
     valarray<int> covariates_data(aux_length_data);
     //valarray<int> class_labels(datos.num_columns);
     valarray<double> exact_p_value(aux_num_rows);

     for (unsigned int m = 0; m < aux_length_data; ++m) covariates_data[m] =static_cast<int>(val_covariates[m]);
     //for (unsigned int m = 0; m < datos.num_columns; ++m) class_labels[m] =static_cast<int>(datos.columns[m]);

     exact_Fisher_p_value_IxJ(exact_p_value, covariates_data,
			      val_columns_int, aux_num_rows,
			      aux_num_columns, val_missing);

     test_statistic = -(exact_p_value);
     test_statistic += 1;
   }
   else if(type_statistic == "Cox") {
     double *covar = new double[aux_length_data];
     double *time = new double[aux_num_columns];
     int *status = new int[aux_num_columns];
     

     for (unsigned int m = 0; m < aux_length_data; ++m) 
       covar[m] = val_covariates[m];

     for (unsigned int m = 0; m < aux_num_columns; ++m) {
       // this is not very efficient: I repeat this at each permutation
       // but this could be done once for the whole program.
      time[m] = val_columns[m];
      status[m] = val_censored_status[m];
      if((status[m] > 1) || (status[m] < 0)) {
	 cout << "error ERROR: censored indicator has to be either 0 (censored) or 1 (death observed). " << endl;
	 cout << "Please read the help and try again."<< endl;
	 exit(1);
      }
     }
     int maxiter = 100;
     double eps = 0.0001;
//     cout <<"       Right before calling compute_cox_statistic " << endl; //zz
     compute_cox_statistic(test_statistic, time, status, covar,
			   aux_num_rows, aux_num_columns, maxiter,
			   eps, val_missing);
     delete [] covar;
     delete [] time;
     delete [] status;
   }
   //  *** The following two tests are disabled, since:
   //  a) Fisher's exact test based test is superior to contin, and is directly
   //     a minP method.
   //  b) "Fisher" is a special case of FisherIxJ; FisherIxJ has more error
   //      checking and might be more efficient. 
//    else if(type_statistic == "contin") {
//      valarray<int> covariates_data(datos.length_data);
//      // valarray<int> class_labels(datos.num_columns);
//      // I don't understand why the following two don't work
//      //covariates_data = static_cast<std::valarray<int> >(datos.covariates);
//      //class_labels = static_cast<std::valarray<int> >(datos.columns);
//      for (unsigned int m = 0; m < datos.length_data; ++m) 
//             covariates_data[m] =static_cast<int>(datos.covariates[m]);
//      //for (unsigned int m = 0; m < datos.num_columns; ++m) 
//                   class_labels[m] =static_cast<int>(datos.columns[m]);
//      compute_test_statistic_2_class(test_statistic,
//                                     covariates_data,
//                                     //class_labels,
// 				    datos.columns_int,
//                                     datos.num_rows,
//                                     datos.num_columns,
//                                     val_missing);
//    }
//    else if(type_statistic == "Fisher") {
//      valarray<int> covariates_data(datos.length_data);
//      //valarray<int> class_labels(datos.num_columns);
//      valarray<double> exact_p_value(datos.num_rows);

//      for (unsigned int m = 0; m < datos.length_data; ++m) 
//               covariates_data[m] =static_cast<int>(datos.covariates[m]);
//      //for (unsigned int m = 0; m < datos.num_columns; ++m) 
//               class_labels[m] =static_cast<int>(datos.columns[m]);
//      exact_Fisher_p_value(exact_p_value, covariates_data,
//                           datos.columns_int, datos.num_rows,
//                           datos.num_columns, val_missing);

//      test_statistic = -(exact_p_value);
//      test_statistic += 1;
//    }
}
void compute_t_test(valarray<double> &test_statistic,
 		    const valarray<double> &data,
 		    const valarray<int> &class_labels,
 		    const int &num_vars, const int &num_HS,
 		    const valarray<int> &MissingArray,
		    const int &number_of_run) {
  static valarray<double> sum_sq(data.size());
  if(number_of_run == 0) sum_sq = data * data; //if number_of_run is the first, 
                                               //  we initialize,
  // and never have to recompute again.

  int i = 0;
  for(int j = 0; j < num_vars; j++) {
    // Loop over variables or genes and do:
    // a) extract the non-missing values and place them in group1 and group2.
    // b) compute the test statistic (t for unequal variances).
    // To use gsl, need to make group1 and group2 into *double, not vector.

    double mean_group1, mean_group2, var_group1, var_group2;
    double sum_sq_1, sum_sq_2, sum_1, sum_2;
    unsigned int size_group1, size_group2;
    sum_sq_1 = 0.0F;
    sum_sq_2 = 0.0F;
    sum_1 = 0.0F;
    sum_2 = 0.0F;
    size_group1 = 0;
    size_group2 = 0;

    int n = 0;
    for(int m = 0; m < num_HS; m++) {
      if(!MissingArray[i + m]) {
	if(class_labels[m]) {
	  sum_sq_2 += sum_sq[i + m];
	  sum_2 += data[i+m];
	  ++size_group2;
	} 
	else {
	  sum_sq_1 += sum_sq[i + m];
	  sum_1 += data[i+m];
	  ++size_group1;
	}
	++n;
      }
    }

    

    if(size_group1 == 0) {
      cout << "error ERROR: size of group 1 is 0 at gene " << j+1 << endl;
      exit(1);
    }
    if(size_group2 == 0) {
      cout << "error ERROR: size of group 2 is 0 at gene " << j+1 << endl;
      exit(1);
    }

    if(size_group1 == 1) {
      cout << "error ERROR: size of group 1 is 1 at gene " << j+1 << endl;
      cout << "This makes it impossible to calculate a variance. Please,\n ";
      cout << "read the help file for a longer explanation." << endl;
      cout << "If you are desperate, you can try using ANOVA, as long as the\n";
      cout << "number of missing values is smaller than the size of"
	   << " the smallest group" << endl;
     exit(1);
    }
    if(size_group2 == 1) {
      cout << "error ERROR: size of group 2 is 1 at gene " << j+1 << endl;
      cout << "This makes it impossible to calculate a variance. Please,\n ";
      cout << "read the help file for a longer explanation." << endl;
      cout << "If you are desperate, you can try using ANOVA, as long as the\n";
      cout << "number of missing values is smaller than the size of"
	   << " the smallest group" << endl;
      exit(1);
    }
 

    mean_group1 = sum_1/size_group1;
    mean_group2 = sum_2/size_group2;
    var_group1 = (sum_sq_1 - (sum_1 * sum_1)/size_group1)/(size_group1 - 1);
    var_group2 = (sum_sq_2 - (sum_2 * sum_2)/size_group2)/(size_group2 - 1);

    if((var_group1 + var_group2) <= 0.0) {
      cout << "error ERROR: sum of variances is 0 at gene " << j + 1;
      cout <<". This should never happen." << endl;
      exit(1);
    }

    test_statistic[j] = 
      (mean_group1 - mean_group2)/
      sqrt((var_group1/size_group1) + (var_group2/size_group2));

//     if(j == 1507) { // for debugging
//       cout << "***************************************\n";
//       cout << " mean_group 1  " << mean_group1 << endl;
//       cout << " mean_group 2  " << mean_group2 << endl;
//       cout << " size_group 1  " << size_group1 << endl;
//       cout << " size_group 2  " << size_group2 << endl;
//       cout << " var_group 1  " << var_group1 << endl;
//       cout << " var_group 2  " << var_group2 << endl;
//       cout << " test statistic " << test_statistic[j] << endl;
//     }

    i += num_HS;
  }
}

void compute_F_test(valarray<double> &test_statistic,
		    const valarray<double> &data,
		    const valarray<int> &class_labels,
		    const int &num_vars, const int &num_HS,
		    const valarray<int> &MissingArray,
		    const int &number_of_run) {
  int i = 0;

  for(int j = 0; j < num_vars; j++) {
    // Loop over variables or genes and do:
    // a) extract the non-missing values and place them in group1 and group2.
    // b) compute the test statistic (t for unequal variances).
    // To use gsl, need to make group1 and group2 into *double, not vector.

    //xx optimize: could move this out of the loop?
    int number_of_groups = class_labels.max() + 1;
    valarray<double> within_group_sum(0.0F, number_of_groups);
    valarray<double> within_group_size(0.0F, number_of_groups); //could be int,
                                  //but would need casting later when dividing.

    double total_sum_squares = 0;
    double x_dot_dot = 0;
    int num_non_missing = 0;

    for(int m = 0; m < num_HS; m++) {
      if(!MissingArray[i + m]) {
     within_group_sum[class_labels[m]] += data[i + m];
     ++within_group_size[ class_labels[m] ];
     total_sum_squares += data[i + m] * data[i + m]; //xx:constant over iterat.
     x_dot_dot += data[i + m]; //xx:constant over iterations; make static
     ++num_non_missing;
      }
    }

    // Checks
    int larger_than_one = 0;
    int larger_than_zero = 0;
    for (int s = 0; s < number_of_groups; ++s) {
      if(within_group_size[s] >= 2) ++larger_than_one;
      if(within_group_size[s] >= 1) ++larger_than_zero;
      }


//     if(larger_than_one <= 1 ) {
//       log_out <<"ERROR: at gene " << j + 1 
// 	      <<" there is only one group with sample size > 1; \n";
//       log_out <<"\t\t this is probably not what you want. \n" << endl;
//       //exit(1);
//     }
    if(larger_than_zero == 0) {
      cout << "ERROR: at gene " << j + 1 
	   << "; no group has any observations." << endl;
//      cout <<"\n This should never happen"<< endl;
//      cout << "Please let us know of this error sending an email to rdiaz@cnio.es" << endl;
      exit(1);
    }
    if(larger_than_zero == 1) {
      cout << "error ERROR: at gene " << j + 1 
	   << "; only one group has any observations." << endl;
//       cout << "\n This should never happen"<< endl;
//       cout << "Please let us know of this error." << endl;
      exit(1);
    }

    // The following stops the program if the size of any
    // group is 0. Note that it is not obvious that this is the
    // only strategy. This is not coherent with what we do with
    // Fisher's test. In general, we need to think about a way
    // to deal with these issues. At least exiting is coherent
    // with what we do now with the t-test, etc, that if
    // anything would given an NA, we exit. 

    for (int s = 0; s < number_of_groups; ++s) {
      if(within_group_size[s] < 1) {
	cout << "ERROR: at gene " << j + 1 
	     << " class " << s + 1 << " has no observations."
	     << endl;
	exit(1);
      }
    }


    within_group_sum *= within_group_sum; //square it
    within_group_sum /= within_group_size;//problem if within_group_size is int
    double group_sum_squares = within_group_sum.sum();
    double x_dot_dot_square_N = x_dot_dot * x_dot_dot/num_non_missing; 
                                           // constant over iterations

    double mean_square_model = 
      (group_sum_squares - x_dot_dot_square_N)/(number_of_groups - 1);

    double mean_square_error = 
      (total_sum_squares - group_sum_squares)/
      (num_non_missing - number_of_groups);

    test_statistic[j] = mean_square_model/mean_square_error;

    i += num_HS;
    ~within_group_sum;
    ~within_group_size;
  }
}



void compute_regression_test(valarray<double> &test_statistic,
		    const valarray<double> &data,
		    const valarray<double> &dependent_var,
		    const int &num_vars, const int &num_subjects,
		    const valarray<int> &MissingArray,
		    const int &number_of_run) {


  int i = 0;

  vector<double> tmp_V_Y(num_subjects);
  vector<double> tmp_V_X(num_subjects);

  for(int j = 0; j < num_vars; j++) {
    int num_non_missing = 0;

    // Place data in neat holders eliminating missing;
//    cout << "\n *********************************** \n";
    for(int m = 0; m < num_subjects; m++) {
      if(!MissingArray[i + m]) {
	tmp_V_X[num_non_missing] = data[i + m];
	tmp_V_Y[num_non_missing] = dependent_var[m];
	++num_non_missing;
      }
    }
    valarray<double> Y(num_non_missing);
    valarray<double> X(num_non_missing);
    for(int m = 0; m < num_non_missing; ++m) {
      Y[m] = tmp_V_Y[m];
      X[m] = tmp_V_X[m];
    }
    
    // Center Y (recall X already centered):
    double SY = Y.sum();
    SY /= num_non_missing;
    Y -= SY;
    

    // The basic pieces
    valarray<double> tmp1 = Y * X;
    double SXY = tmp1.sum();
    for(int m = 0; m < num_non_missing; ++m) tmp1[m] = X[m] * X[m];
    double SX2 = tmp1.sum();
    for(int m = 0; m < num_non_missing; ++m) tmp1[m] = Y[m] * Y[m];
    double SY2 = tmp1.sum();

    // Do in two pieces, just in case denominator is weird:
    double denominator = sqrt((SX2 * SY2 - (SXY*SXY)) / (num_non_missing - 2));
    if (denominator == 0) {
      cout << "ERROR: the denominator for gene " << j + 1 
	   << " for t statistic for regression is 0.\n";
      cout << " This should never happen" << endl;
      exit(1);
    }
    test_statistic[j] = SXY/denominator;

    i += num_subjects;
    ~X;
    ~Y;
    ~tmp1;
  }
}


double test_statistic_two_proportions(const std::valarray<int> &data,
			const std::valarray<int> &class_labels_0,
			const std::valarray<int> &class_labels_1,
			const int &n_0,	const int &n_1) {
/*  Compares two proportions, using a test statistic
		that is equivalent to Fisher's exact test.
  	OK, so it is just the difference in proportions... */

  double sum_0, sum_1, mean_0, mean_1, test_statistic;
  sum_0 = sum_1 = 0;
  sum_0 = inner_product(&data[0], &data[data.size()], &class_labels_0[0], 0);
  sum_1 = inner_product(&data[0], &data[data.size()], &class_labels_1[0], 0);
  mean_0 = sum_0/n_0;
  mean_1 = sum_1/n_1;

  test_statistic = mean_0 - mean_1;
  return test_statistic;
}




void compute_test_statistic_2_class(valarray<double> &test_statistic,
			    const valarray<int> &data,
			    const valarray<int> &class_labels,
			    const int &num_vars, const int &num_HS,
			    const valarray<int> &MissingArray) {
/*	Obtain the tests statistic for all the rows (variables).
		in the 2-class situation.
  	The function for computing the test statistic is
   	hard-coded; xx:fix this situation? Nope, this is old code,
	only used now for research of the contingency table
	statistic. For real cases, use Fisher.
    */

  // Obtain a vector with 1 in positions of class0.
  valarray<int> class_labels_0(num_HS);
  class_labels_0 = class_labels;
  class_labels_0 -= 1;
  class_labels_0 *= (-1);

  int i = 0;
  //Loop over vars, or "rows" in the  original matrix
  for(int j = 0; j < num_vars; j++) {
    int num_non_missing = num_HS - MissingArray[slice(i,num_HS, 1)].sum();
    valarray<int> tmp_data(num_non_missing);
    valarray<int> tmp_class_labels(num_non_missing);
    valarray<int> tmp_class_labels_0(num_non_missing);

    // xx:Deal with missing: assign values to the temporaries
    // only if non-missing.
    // There are ways of doing this were I don't need to repeat
    // this step at each iteration, but I would need to change
    // the loops. We'll see if it is needed when profiling.

    int n = 0;
    for(int m = 0; m < num_HS; m++) {
      if(!MissingArray[i + m]) {
         tmp_data[n] = data[i + m];
         tmp_class_labels[n] = class_labels[m];
         tmp_class_labels_0[n] = class_labels_0[m];
         ++n;
      }
    }
    int tmp_n_0 = tmp_class_labels_0.sum();
    int tmp_n_1 = tmp_class_labels.sum();

    test_statistic[j] = test_statistic_two_proportions(tmp_data, tmp_class_labels_0,
						       tmp_class_labels, tmp_n_0,
						       tmp_n_1);

    i += num_HS;
  }
}


void exact_Fisher_p_value(valarray<double> &exact_p_value,
			    const valarray<int> &data,
			    const valarray<int> &class_labels,
			    const int &num_vars, const int &num_HS,
 			    const valarray<int> &MissingArray){
  // This is specific for 2x2 tables.
  // The code for IxJ is more general (and, of course,
  // includes 2x2 as special case), and has more error
  // checking of degenerate cases.

  double contingency_table[4] = {0, 0, 0, 0};
  //stuff for Fisher's test
  int nrow = 2;
  int *nrowp = &nrow;
  int ncol = 2;
  int *ncolp = &ncol;
  double expected = -1.0;
  double percnt = 100.0;
  double emin = 0.0;
  double prt = 0.0;
  double *expectedp = &expected;
  double *percntp = &percnt;
  double *eminp = &emin;
  double *prtp = &prt;
  double pvalue = 0.0;
  double *pvaluep = &pvalue;
  int workspace = 300000;
  int *workspacep = &workspace;

  int i = 0;
  for(int j = 0; j < num_vars; j++) {
    int num_non_missing = num_HS - MissingArray[slice(i,num_HS, 1)].sum();
    valarray<int> tmp_data(num_non_missing);
    valarray<int> tmp_class_labels(num_non_missing);
    // Deal with missing: assign values to the temporaries
    // only if non-missing.
    // Do it as follows:
//       a vector with length of each "row" without missing
//       a vector with position of missing
//       the loop in jumps not of num_HS, but of number of non-missing per row.
//       eliminate the value of class_label corresponding to the missing
//       position.
//       the first tow not necessary in a per loop basis.
    int n = 0;
    for(int m = 0; m < num_HS; m++) {
      if(!MissingArray[i + m]) {
         tmp_data[n] = data[i + m];
         tmp_class_labels[n] = class_labels[m];
         ++n;
      }
    }


    for (int m = 0; m < 4; m++) contingency_table[m] = 0;
    for (int k = 0; k < num_non_missing; k++) {
      if((tmp_class_labels[k] == 0) && (tmp_data[k] == 0)) 
	++contingency_table[0];
      else if((tmp_class_labels[k] == 0) && (tmp_data[k] == 1)) 
	++contingency_table[1];
      else if((tmp_class_labels[k] == 1) && (tmp_data[k] == 0)) 
	++contingency_table[2];
      else ++contingency_table[3];
    }
    pvalue = 0;
    fexact(nrowp, ncolp, contingency_table, nrowp, expectedp, percntp, 
	   eminp, prtp, pvaluep, workspacep);
   exact_p_value[j] = pvalue;
    i += num_HS;
  }
}




void exact_Fisher_p_value_IxJ(valarray<double> &exact_p_value,
			      const valarray<int> &data,
			      const valarray<int> &class_labels,
			      const int &num_vars, const int &num_HS,
			      const valarray<int> &MissingArray){
// p-value from Fisher's exact test for tables IxJ.

  //stuff for Fisher's test
  double expected = -1.0;
  double percnt = 100.0;
  double emin = 0.0;
  double prt = 0.0;
  double *expectedp = &expected;
  double *percntp = &percnt;
  double *eminp = &emin;
  double *prtp = &prt;
  double pvalue = 0.0;
  double *pvaluep = &pvalue;
  int workspace = 300000;
  int *workspacep = &workspace;

  int i = 0;
  for(int j = 0; j < num_vars; j++) {
    int num_non_missing = num_HS - MissingArray[slice(i,num_HS, 1)].sum();
    valarray<int> tmp_data(num_non_missing);
    valarray<int> tmp_class_labels(num_non_missing);
    // Deal with missing: assign values to the temporaries
    // only if non-missing.
    // Do it as follows:
//     a vector with length of each "row" without missing
//     a vector with position of missing
//     the loop in jumps not of num_HS, but of number of non-missing per row.
//     eliminate the value of class_label corresponding to the missing
//     position.
//     the first tow not necessary in a per loop basis.
    int n = 0;
    for(int m = 0; m < num_HS; m++) {
      if(!MissingArray[i + m]) {
         tmp_data[n] = data[i + m];
         tmp_class_labels[n] = class_labels[m];
         ++n;
      }
    }

    // nrow is the number of categories or values that can be taken
    // ncol is the number of classes in the data.
    int nrow = tmp_class_labels.max() + 1;
    int ncol = tmp_data.max() + 1;    
    int *nrowp = &nrow;
    int *ncolp = &ncol;
    

    double *contingency_table = new double[nrow * ncol];
    for(int n = 0; n < (nrow * ncol); ++n) contingency_table[n] = 0; 
    
    // each of the cells positions in the contingency table,
    // if we use column major order, is: 
    //     category + (number of categories * (class - 1))
    // or 
    //     row + (number of rows * (column - 1))
    // if categories and classes numbered from 0, formula is:
    //    row +  (number of rows * column)

    for (int k = 0; k < num_non_missing; ++k) {
      ++contingency_table[ tmp_class_labels[k] + (nrow * tmp_data[k] )];
    }

    pvalue = 0;
    if((nrow >= 2) && (ncol >= 2)) 
      fexact(nrowp, ncolp, contingency_table, nrowp, expectedp, 
	     percntp,eminp, prtp, pvaluep, workspacep);
    else {
      pvalue = 1;
      //log_out << "\n Degenerate table for variable " << j <<". P-value set to 1." << endl;
    }
   exact_p_value[j] = pvalue;
   delete[] contingency_table;
   i += num_HS;
  }
}



void order_observed_statistics(valarray<unsigned int> &order_stat_decreasing,
			       valarray<double> &ordered_observed_test_statistic,
			       const valarray <double> &observed_test_statistic,
			       const int &num_vars) {
// Here we:
  // a) order the observed test statistics;
  // b) return the vector of indexes such that the statistics would be ordered
      // from largest to smalles (equivalent to R's command
      //  order(vector, decreasing = FALSE).

// This code is ugly and redundant, and could probably be made faster
// if we operate directly on valarrays.


  double* const copy_of_observed_statistic = new double[num_vars];
  if(! copy_of_observed_statistic) {
    cout << "ERROR in order_observed_statistic: \n"
	 <<"      allocation failure in copy_of_observed_statistic\n";
    exit(1);
  }
  size_t* order_stat = new size_t[num_vars];
  if(! copy_of_observed_statistic) {
    cout << "ERROR in order_observed_statistics: \n"
	 <<"        allocation failure in order_stat\n";
    exit(1);
  }

  for(int i = 0; i < num_vars; i++)
    copy_of_observed_statistic[i] = abs(observed_test_statistic[i]);

 gsl_sort_index(order_stat, copy_of_observed_statistic, 1, num_vars);

 for(int i = 0; i < num_vars; i++) {
   order_stat_decreasing[i] = order_stat[((num_vars -1) - i)];
   ordered_observed_test_statistic[i] =
     abs(observed_test_statistic[order_stat_decreasing[i]]);
    }

 delete [] copy_of_observed_statistic;
 delete [] order_stat;
}

void increase_unadjusted_p_value_counter(valarray <unsigned long int> 
					   &counter_unadjusted_p_value,
					 const valarray <double> 
					   &permuted_test_statistic,
					 const valarray <double> 
					   &ordered_observed_test_statistic,
					 const valarray <unsigned int> 
					   &order_stat_decreasing,
					 const int &num_vars) {
/* I increase the p_value_counter at each iteration
   (each of the random shuffles or each of the sistematic
   shuffles).

   The unadjusted p-values and counter refer to the ordered
   data (ordered by observed test statistic).
*/

  for (int i = 0; i < num_vars; i++) {
    if((abs(permuted_test_statistic[order_stat_decreasing[i]]) + fuzz_factor) >= 
       ordered_observed_test_statistic[i])
      ++counter_unadjusted_p_value[i];
  }
}


void increase_adjusted_p_value_counter(valarray <unsigned long int> 
				         &counter_adjusted_p_value,
				       const valarray <double> 
				         &permuted_test_statistic,
				       const valarray <double> 
				         &ordered_observed_test_statistic,
				       const valarray <unsigned int> 
				         &order_stat_decreasing,
				       const int &num_vars) {
/* I increase the p_value_counter at each iteration
   (each of the random shuffles or each of the sistematic
   shuffles).
   I compute the u's as the algorithm in Dudoit, but
   I increase the conter at each iteration, in contrast
   to Dudoit */

  // Get the vector of u's.
  valarray<double> u_vector(num_vars);
  for (int i = 0; i < num_vars; i++)
    u_vector[i] = abs(permuted_test_statistic[order_stat_decreasing[i]]);
  for (int i = (num_vars - 2); i >= 0; i--) {
    u_vector[i] = max(u_vector[(i + 1)], u_vector[i]);
  }

  //  See if the u is larger than the correponding test statistic.
     for(int i = 0; i < num_vars; i++) {
       if((u_vector[i] + fuzz_factor) >= ordered_observed_test_statistic[i])
	 ++counter_adjusted_p_value[i];
     }
}



void FDR_p_value(valarray <double> &FDR_indep_p_values,
		 valarray <double> &FDR_dep_p_values,
		 const valarray<double> unadjusted_p_value,
		 const int num_vars,
		 const valarray <unsigned int> &order_stat_decreasing) {
// Gives the two types of FDR:
  // - indep p-values
  // - arbitrary dependence struct.

  size_t* order_unadjusted_p_value = new size_t[num_vars];
  double* const tmp_p = new double[num_vars];
  for(int i = 0; i < num_vars; i++) tmp_p[i] = unadjusted_p_value[i];

  valarray<double> reordered_unadjusted_p_values(num_vars);
  valarray<double> min_prod_k(num_vars);
  valarray<double> min_prod_k_2(num_vars);
  valarray<double> tmp_FDR_dep_p_values(num_vars);
  valarray<double> tmp_FDR_indep_p_values(num_vars);

  gsl_sort_index(order_unadjusted_p_value, tmp_p, 1, num_vars);

  for (int m = 0; m < num_vars; m++)
    reordered_unadjusted_p_values[m] = 
      unadjusted_p_value[order_unadjusted_p_value[m]];

  // xx: make this more efficiente by combining the loops?

// Independent FDR
  for (int k = 0; k < num_vars; k++)
    min_prod_k[k] = min(1.0, reordered_unadjusted_p_values[k] * 
			static_cast<double>(num_vars)/(k+1));
  for (int j = 0; j < num_vars; j++) {
    valarray<double> tmp_dat = min_prod_k[slice(j, num_vars - j, 1)];
    tmp_FDR_indep_p_values[j] = tmp_dat.min();
  }

// Arbitrary dep. FDR.
  double tmp1 = 1;
  for(int j = 2; j <= num_vars; j++) tmp1 += 1/static_cast<double>(j); 
                                       //para esto hay formula seguro.
  for (int k = 0; k < num_vars; k++)
    min_prod_k_2[k] = min(1.0, reordered_unadjusted_p_values[k] * tmp1 * 
			  static_cast<double>(num_vars)/(k+1));
  for (int j = 0; j < num_vars; j++) {
    valarray<double> tmp_dat = min_prod_k_2[slice(j, num_vars - j, 1)];
    tmp_FDR_dep_p_values[j] = tmp_dat.min();
  }

// Return the FDR adjusted p-values in same order as the maxT adjusted ones.
   for(int i = 0; i < num_vars; i++) {
     int j = order_unadjusted_p_value[i];
     FDR_dep_p_values[j]   = tmp_FDR_dep_p_values[i];
     FDR_indep_p_values[j] = tmp_FDR_indep_p_values[i];
   }

  delete [] order_unadjusted_p_value;
  delete [] tmp_p;
}










