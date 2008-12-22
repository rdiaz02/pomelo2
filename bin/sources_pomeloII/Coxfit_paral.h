
/***************************************************************************
    copyright            : (C) 2002 - 2009 by Ramón Díaz-Uriarte
    email                : rdiaz02@gmail.com
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







#ifndef GUARD_Coxfit_h
#define GUARD_Coxfit_h

// permute_covars should be in multestutil
// covariate centering y all_covariate_centering en multestutil

#include<valarray>
#include<fstream>
void permute_covars(std::valarray<double> &covariate, 
		    std::valarray<int> &missing,
		    std::valarray<int> &order_vector, 
		    const int &num_genes,
		    const int &num_subjects);

//void covariate_centering(double *covar, const int &nused);

void all_covariates_centering(std::valarray<double> &covariates, 
			      const std::valarray<int> &missing,
			      const int num_subjects, 
			      const int num_genes);

void sort_for_survival(const int &num_subjects, const int &num_genes, 
		       const int &length_data,
		       std::valarray<double> &survival_time, 
		       std::valarray<int> &censored_status, 
		       std::valarray<double> &covar,
		       std::valarray<int> &missing);

void coxfit2(int   &maxiter, const int &nusedx, const double *time,
	     const int   *status, const double *covar, double &beta, 
	     double &imat, double *loglik,  int   &flag, 
	     const double &eps, double &u); 

void compute_cox_statistic(std::valarray<double> &test_statistic,
			   const double *time, const int *status, 
			   const double  *covar,
			   const int &num_genes, 
			   const int &num_subjects,
			   const int &maxiter, const double &eps,
			   const std::valarray<int> &MissingArray);
#endif
