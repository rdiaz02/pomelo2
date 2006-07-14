/***************************************************************************
                          multestutil.h  -  description
                             -------------------
    begin                : Wed Jul 17 2002
    copyright            : (C) 2002 by Ramon Diaz
    email                : rdiaz@cnio.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifndef GUARD_multestutil
#define GUARD_multestutil

#include<valarray>
#include<string>
#include<gsl/gsl_math.h>
#include<gsl/gsl_rng.h>
#include<gsl/gsl_randist.h>
#include<gsl/gsl_statistics_double.h>
#include"readMissing.h" //need to know about input_data_struct
#include"Coxfit_paral.h"

void compute_test_statistic(unsigned int       aux_length_data,
			    unsigned int       aux_num_columns,
			    unsigned int       aux_num_rows,
			    std::valarray<int>      val_missing,
			    std::valarray<double>   val_covariates,
			    std::valarray<double>   val_columns,
			    std::valarray<int>      val_columns_int,
			    std::valarray<int>      val_censored_status,
                            std::valarray<double> &test_statistic,
                            std::string type_statistic,
			    const int &number_of_run);
/* A very general wrapper for all the specific ways to
   obtain the test statistics and p-values.  This is most likely
   the place where you will add your own code (maybe also calling
   functions for the specifics of the p-value computation)*/

void compute_t_test(std::valarray<double> &test_statistic, 
 		    const std::valarray<double> &data, 
 		    const std::valarray<int> &class_labels, 
 		    const int &num_vars, const int &num_HS, 
 		    const std::valarray<int> &MissingArray,
		    const int &number_of_run); 

/* void compute_t_test(std::valarray<double> &test_statistic, */
/* 		    const std::valarray<double> &data, */
/* 		    const std::valarray<double> &class_labels, */
/* 		    const int &num_vars, const int &num_HS, */
/* 		    const std::valarray<int> &MissingArray); */

double test_statistic_two_proportions(const std::valarray<int> &data,
			const std::valarray<int> &class_labels_0,
			const std::valarray<int> &class_labels_1,
			const int &n_0,	const int &n_1);
/*  Compares two proportions, using a test statistic
		that is equivalent to Fisher's exact test.
  	OK, so it is just the difference in proportions... */

void compute_test_statistic_2_class(std::valarray<double> &test_statistic,
			    const std::valarray<int> &data,
			    const std::valarray<int> &class_labels,
			    const int &num_vars, const int &num_HS,
//			    const int &n_0, const int &n_1,
			    const std::valarray<int> &MissingArray);
/*	Obtain the tests statistic for all the rows (variables).
		in the 2-class situation.
  	The function for computing the test statistic is
   	hard-coded   */

void exact_Fisher_p_value(std::valarray<double> &exact_p_value,
			    const std::valarray<int> &data,
			    const std::valarray<int> &class_labels,
			    const int &num_vars, const int &num_HS,
 			    const std::valarray<int> &MissingArray);
/* p-value with Fisher's exact text for 2x2 tables*/

void exact_Fisher_p_value_IxJ(std::valarray<double> &exact_p_value,
			      const std::valarray<int> &data,
			      const std::valarray<int> &class_labels,
			      const int &num_vars, const int &num_HS,
			      const std::valarray<int> &MissingArray);
// p-value from Fisher's exact test for tables IxJ.

void order_observed_statistics(std::valarray <unsigned int> 
			         &order_stat_decreasing,
			       std::valarray <double> 
			         &ordered_observed_test_statistic,
			       const std::valarray <double> 
			         &observed_test_statistic,
			       const int &num_vars);
// Here we:
  // a) order the observed test statistics;
  // b) return the vector of indexes such that the statistics would be ordered
      // from largest to smalles (equivalent to R's command
      //  order(vector, decreasing = FALSE).


void increase_unadjusted_p_value_counter(std::valarray <unsigned long int> 
					   &counter_unadjusted_p_value,
					 const std::valarray <double> 
					   &permuted_test_statistic,
					 const std::valarray <double> 
					   &ordered_observed_test_statistic,
					 const std::valarray <unsigned int> 
					   &order_stat_decreasing,
					 const int &num_vars);
/* I increase the p_value_counter at each iteration
   (each of the random shuffles or each of the sistematic
   shuffles).

   The unadjusted p-values and counter refer to the ordered
   data (ordered by observed test statistic).
*/


void increase_adjusted_p_value_counter(std::valarray <unsigned long int> 
				         &counter_adjusted_p_value,
				       const std::valarray <double> 
				         &permuted_test_statistic,
				       const std::valarray <double> 
				         &ordered_observed_test_statistic,
				       const std::valarray <unsigned int> 
				        &order_stat_decreasing,
				       const int &num_vars);

void FDR_p_value(std::valarray <double> &FDR_indep_p_values,
		 std::valarray <double> &FDR_dep_p_values,
		 const std::valarray<double> unadjusted_p_value,
		 const int num_vars,
		 const std::valarray <unsigned int> &order_stat_decreasing);
// Gives the two types of FDR:
  // - indep p-values
  // - arbitrary dependence struct.

void compute_F_test(std::valarray<double> &test_statistic,
		    const std::valarray<double> &data,
		    const std::valarray<int> &class_labels,
		    const int &num_vars, const int &num_HS,
		    const std::valarray<int> &MissingArray,
		    const int &number_of_run);

void compute_regression_test(std::valarray<double> &test_statistic,
			     const std::valarray<double> &data,
			     const std::valarray<double> &dependent_var,
			     const int &num_vars, const int &num_subjects,
			     const std::valarray<int> &MissingArray,
			     const int &number_of_run);


#endif

