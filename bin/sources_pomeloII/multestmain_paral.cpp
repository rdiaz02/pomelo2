/***************************************************************************
    multestmain_paral.cpp: main program for multiple testing adjustments.
***************************************************************************/ 
/***************************************************************************
    begin                : Thu Jul 11 19:21:37 CEST 2002
    copyright            : (C) 2002, 2003, 2004 by Ramón Díaz-Uriarte,
                               2005-2009  by Edward R. Morrissey and
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

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#ifdef DEBUG
 #define PR(x) cout << #x " = " << x << endl;
#else
 #define PR(x);
#endif

#include"readMissing.h"
#include"multestutil_paral.h"
#include"Coxfit_paral.h"

// xx: ATLAS y BLAS?
#include <mpi.h> // Parallel processing library
#include<iostream>
#include<cstdlib>
#include<algorithm>
#include<numeric>
#include<vector>
#include<fstream>
#include<string>
#include<valarray>
#include<ctime> //to seed the random number generators, if no seed is given
#include<cmath>
#include<sstream> // He metido esto para la funcion print_data_struct

#include<gsl/gsl_math.h>
#include<gsl/gsl_rng.h>
#include<gsl/gsl_randist.h>
#include<gsl/gsl_sort_double.h>
//#include<gsl/gsl_combination.h>
//#include<gsl/gsl_sf_gamma.h> //To obtain choose(m,k);

using namespace std;


template <class Ran>
void random_shuffle_3(Ran first, Ran last, const gsl_rng *r) {
  // Copied from stl_algo.h, but I modify the call to the random number
  // generator to have control over it.
  if (first == last) return;
  for (Ran i = first + 1; i != last; ++i)
    iter_swap(i, first + gsl_rng_uniform_int(r, ((i - first) + 1)));
}


// some sorting utilities
struct my_sort_struct{
  int the_int;
  double the_double;
};


bool my_sort_struct_compare_larger(const my_sort_struct x, 
				   const my_sort_struct y) {
  return x.the_double > y.the_double;
}

valarray<double> double_count_larger_equal(const valarray<double> &v2) {
// We have a valarray that contains test statistics. For each one, we
// want to know how many are larger or equal (to get the p-value).
// (This code substitutes a quadratic time algorithm that, in each position,
// looks at the value of all other positions and adds to the counter if
// larger or equal.)
// If all test statistics were different, we would only need to sort
// the data, and get, as value, the sorted position + 1.
// If test statistics can be equal, we first sort, and then check if
// for a given sorted position the next positions are equal. If they are, then
// the value returned is the largest sorted position of the values that
// are equal.
// Finally, we return the values in the original order given.


// *************Do the sorting.**************************************** 
// Create a dummy int valarray (v1) to identify the original order.
  valarray<int> v1(v2.size());
  for(unsigned int  i = 0; i < v2.size(); ++i) v1[i] = i; 

// Create a structure so that we sort the doubles and move also the
// dummy ints.
  vector<my_sort_struct> structura(v1.size());
  for(unsigned int i = 0; i < v1.size(); ++i) {
    structura[i].the_int = v1[i];
    structura[i].the_double = v2[i];
  }
  sort(structura.begin(), structura.end(), my_sort_struct_compare_larger);
  



//********** Count larger or equal ************************************
  // The code to counter number of larger or equal in
  // a sorted valarray or vector v2.

  valarray<int> number_larger_equal(v2.size());
  int i = 0;
  int last_position = v2.size() - 1;
  while(i < last_position) {
      int initial_i = i;
      while(structura[i].the_double == structura[i + 1].the_double) {
	++i;
	if (i == last_position) break;
      }
      for (int j = initial_i; j <= i; ++j) {
	number_larger_equal[j] = i + 1;
      }
      ++i;
  }
  number_larger_equal[last_position] = last_position + 1;

//********** Return in original order ************************************
  valarray<double> return_number_larger_equal(v2.size());
  for(unsigned int i = 0; i < v2.size(); ++i) 
    return_number_larger_equal[ structura[i].the_int ] = 
      static_cast<double>(number_larger_equal[i]);

  return return_number_larger_equal;
}


int main(int argc, char *argv[])
{
	int                     rank;
	int                     matrix_position, int_row_test;
	unsigned int            i_loop, col_loop, row_loop, end_loop, cpu_loop,numberOFcpu;
	unsigned int            aux_length_data, matrix_size;
	unsigned int            aux_num_columns;
	unsigned int            aux_num_rows;
	int                     *aux_missing;
	double                  *aux_covariates;
	double                  *aux_columns; //continuous data
	int                     *aux_columns_int; //For t, anova, contin, Fisher, FisherIxJ
	int                     *aux_censored_status;
	int			aux_iscensored;
	int			aux_isinteger;
	int			aux_ismissing;
	vector<string>          aux_ID;
	valarray<int>           val_missing;
	valarray<double>        val_covariates;
	valarray<double>        val_columns; 
	valarray<int>           val_columns_int; 
	valarray<int>           val_censored_status;
	int			*matrix_rndm_columns_int;
	int			*matrix_rndm_order_vector;	
	double			*matrix_rndm_columns;
	unsigned long int	*aux_counter_adjusted;
	unsigned long int	*aux_counter_unadjusted;
	unsigned long int	*sum_counter_adjusted;
	unsigned long int	*sum_counter_unadjusted;

        // Initialize the MPI environment
	MPI::Init(argc,argv);
	rank = MPI::COMM_WORLD.Get_rank();
	numberOFcpu = MPI::COMM_WORLD.Get_size();

	if(numberOFcpu < 2) {
	    cout << "ERROR: this is a parallelized program. " << endl;
	    cout << "       At least two CPUs are needed, " << endl;
	    cout << "       but only one is available. " << endl;
	    exit(1);
	  }


	// Get number of permutations input by user, calculate number of permutations 
	// per node (matrix num rows) and recalculate total permutations. 
	unsigned int aux_num_permut= static_cast<unsigned int> (atoi(argv[3]));
	unsigned int matrix_numrows = static_cast<unsigned int>(ceil(atof(argv[3])/(numberOFcpu-1)));
//	unsigned int matrix_numrows = static_cast<unsigned int>(std::floor(aux_num_permut/(numberOFcpu-1)));
	unsigned int num_permut     = matrix_numrows*(numberOFcpu-1);

	// Some general variables
	string test_type = argv[1];
	string minP = argv[2];
	bool survival_data = false;
        unsigned long int seed_r = time(0);


   if (rank==0)
   {
    if((argc != 7) && (argc != 6)) {

      cout << "\n\nPomelo, v.1.1, a program to find differentially expressed genes, \n";
      cout << "including multiple testing adjustments.\n";
      cout << "\nCopyright, (C),  2002-2004, by Ramón Díaz-Uriarte \n";
      cout << "\n2005, 2006 by Edward R. Morrissey and Ramón Díaz-Uriarte \n";
      cout << "(Other files copyright of their respective authors. Please\n";
      cout << "see the README file for details. You should have received the\n";
      cout << "README file along with the source code.)\n";
      cout << "\n email: rdiaz@cnio.es; URI: http://ligarto.org/rdiaz\n\n\n";
      cout <<"*************************************************************************\n";
      cout <<"                                                                 \n";
      cout <<"This program is free software; you can redistribute it and/or modify  \n";
      cout <<"it under the terms of the GNU General Public License as published by  \n";
      cout <<"the Free Software Foundation; either version 2 of the License, or     \n";
      cout <<"(at your option) any later version.                                   \n";
      cout <<"\n";
      cout <<"This program is distributed in the hope that it will be useful,        \n";
      cout <<"but WITHOUT ANY WARRANTY; without even the implied warranty of         \n";
      cout <<"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          \n";
      cout <<"GNU General Public License for more details.                           \n";
      cout <<"\n";
      cout <<"You should have received a copy of the GNU General Public License      \n";
      cout <<"along with this program; if not, write to the Free Software            \n";
      cout <<"Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,USA \n";
      cout <<"                                                                        \n";
      cout <<"*************************************************************************\n";
      cout <<"\n\n USAGE:";
     cout <<"\n multest test maxT/minP nperm covariate_data class_data"
	  <<" [censored_data]\n";
     cout <<"\n   test:  type of test; one of:";
     cout <<"\n      FisherIxJ: minP Fisher's exact test for IxJ contingency\n"
	  <<"                         tables (I, J >= 2);";
     cout <<"\n      t:         t-test (welch's);";
     cout <<"\n      Anova:     ANOVA;";
     cout <<"\n      Cox:       Cox regression (survival analysis);";
     cout <<"\n      Regres:    linear regression;";
//      cout <<"\n     Regr2:     quadratic regression;";
//      cout <<"\n     RegrLX:    regression, log-transf. X;";
//      cout <<"\n     RegrLX:    regression, log-transf. Y;";
//      cout <<"\n     RegrLXLY:  regression, log-transf. X & Y;";
//    The following could be made available again, but are disabled now
//    in multestutil.cpp.
//     cout <<"\n     Fisher:    minP Fisher's exact test for 2x2 tables;";
//     cout <<"\n     contin:    maxT for 2x2 tables (not recommended)";
     cout <<"\n\n";
     cout <<"\n   maxT/minP:      whether to use minP or maxT \n";
     cout <<"          (with Fisher's it is always minP; otherwise you \n";
     cout <<"           most likely want maxT) \n";
     cout <<"\n   nperm:          number of permutations";
     cout <<"\n   covariate_data: rows are genes, columns are conditions.";
     cout <<"\n   class_data:     classification or dependent variable"
	  <<" (regression, Cox).";
     cout <<"\n   [censored_data]: if survival data, the censoring indicator.";
     cout <<"\n \n \n" << endl;
     return 1;
     }
   }

  string s2;
  s2 = "multest_parallel.res";

  if(test_type == "FisherIxJ") minP = "Fisher's exact test (minP)"; //to avoid calling minP
  if(argc == 7) survival_data = true;
  else survival_data = false;


  // MASTER reads data and dumps all valarrays to normal arrays that can be sent via mpi
  if (rank==0)
   {

/**************************************************************
 *****                                                   ******
 *****         Read data and set the data class          ******
 *****                                                   ******
 **************************************************************/

  ifstream data_stream(argv[4]);
  ifstream class_stream(argv[5]);
  ifstream censored_stream(argv[6]);

  if( !data_stream ) {
    cout << "ERROR: cannot open covariate data file" << endl;
    exit(1);
  }

  if( !class_stream ) {
    cout << "ERROR: cannot open class labels data file" << endl;
    exit(1);
  }

  ofstream started_ok("mpiOK");
  started_ok << "Multest has started correctly";
  started_ok.close();

  // Instanciate read data object 
  input_data_struct datos(data_stream, class_stream, censored_stream, test_type);


   // Get number of rows and columns. MASTER allocates memory size to each array
   aux_num_columns=datos.num_columns;
   aux_num_rows=datos.num_rows;
   aux_length_data =  aux_num_rows * aux_num_columns;
   aux_covariates = new double [aux_length_data];
   aux_columns = new double [aux_num_columns];
   aux_columns_int = new int [aux_num_columns];
   aux_censored_status = new int [aux_num_columns];
   aux_missing = new int [aux_length_data];

   // Get aux variables that will control whether arrays are empty at broadcast time
   aux_iscensored = (datos.censored_status.size()==0)? 0 : 1;
   aux_isinteger  = (datos.columns_int.size()==0)? 0 : 1;
   aux_ismissing  = (datos.missing.size()==0)? 0 : 1;

   //Dump valarrays
   for ( i_loop=0 ; i_loop<aux_length_data ; i_loop++ ) aux_covariates[i_loop]=datos.covariates[i_loop]; 
   end_loop=datos.columns.size();
   for ( i_loop=0 ; i_loop<end_loop ; i_loop++ ) aux_columns[i_loop]=datos.columns[i_loop]; 
   end_loop=datos.columns_int.size();
   for ( i_loop=0 ; i_loop<end_loop ; i_loop++ ) aux_columns_int[i_loop]=datos.columns_int[i_loop]; 
   end_loop=datos.censored_status.size();
   for ( i_loop=0 ; i_loop<end_loop ; i_loop++) aux_censored_status[i_loop]=datos.censored_status[i_loop]; 
   end_loop=datos.missing.size();
   for ( i_loop=0 ; i_loop<datos.missing.size()  ; i_loop++ ) aux_missing[i_loop]=datos.missing[i_loop]; 
   aux_ID = datos.ID;
}

//********************************************** MAIN DATA DISTRIBUTION START ***************************************

  //MASTER broadcasts number of rows and columns as well as three integers that represent booleans 
  MPI::COMM_WORLD.Bcast(&aux_num_rows,1,MPI::UNSIGNED,0);
  MPI::COMM_WORLD.Bcast(&aux_num_columns,1,MPI::UNSIGNED,0);
  MPI::COMM_WORLD.Bcast(&aux_iscensored,1,MPI::INT,0);
  MPI::COMM_WORLD.Bcast(&aux_isinteger,1,MPI::INT,0);
  MPI::COMM_WORLD.Bcast(&aux_ismissing,1,MPI::INT,0);

 // Slaves resize their dynamic arrays
 if (rank!=0)
 {
     aux_length_data 	  =  aux_num_rows * aux_num_columns;
     aux_covariates 	  = new double [aux_length_data];
     aux_columns 	  = new double [aux_num_columns];
     aux_columns_int 	  = new int [aux_num_columns];
     aux_censored_status  = new int [aux_num_columns];
     aux_missing 	  = new int [aux_length_data];
 }

  // MASTER broadcasts arrays
  MPI::COMM_WORLD.Bcast(aux_covariates,aux_length_data,MPI::DOUBLE,0);
  if (aux_isinteger==0)  MPI::COMM_WORLD.Bcast(aux_columns,aux_num_columns,MPI::DOUBLE,0);
  if (aux_isinteger==1)  MPI::COMM_WORLD.Bcast(aux_columns_int,aux_num_columns,MPI::INT,0);
  if (aux_iscensored==1) MPI::COMM_WORLD.Bcast(aux_censored_status,aux_num_columns,MPI::INT,0);
  if (aux_ismissing==1)  MPI::COMM_WORLD.Bcast(aux_missing,aux_length_data,MPI::INT,0);

  // Transform arrays to valarrays
  val_covariates.resize(aux_length_data);
  for ( i_loop=0 ; i_loop<aux_length_data ; i_loop++ ) val_covariates[i_loop]=aux_covariates[i_loop];
  if (aux_isinteger==0){
	val_columns.resize(aux_num_columns);
	for ( i_loop=0 ; i_loop<aux_num_columns ; i_loop++ ) val_columns[i_loop]=aux_columns[i_loop]; 
  }
  if (aux_isinteger==1){
	val_columns_int.resize(aux_num_columns);
	for ( i_loop=0 ; i_loop<aux_num_columns ; i_loop++ ) val_columns_int[i_loop]=aux_columns_int[i_loop]; 
  }
  if (aux_iscensored==1){
	val_censored_status.resize(aux_num_columns);
	for ( i_loop=0 ; i_loop<aux_num_columns ; i_loop++ ) val_censored_status[i_loop]=aux_censored_status[i_loop]; 
  }
  if (aux_ismissing==1){
	val_missing.resize(aux_length_data);
	for ( i_loop=0 ; i_loop<aux_length_data ; i_loop++ ) val_missing[i_loop]=aux_missing[i_loop]; 
  }

  // Deallocate dynamic memory
  delete[] aux_covariates;
  delete[] aux_columns;
  delete[] aux_columns_int;
  delete[] aux_censored_status;
  delete[] aux_missing;

  // Resize matrixs that will be sent to each node
  matrix_size = aux_num_columns * matrix_numrows;
  // We can now dimension our matrix that will contain the randomly shuffled elements as rows.
  if (test_type == "Cox") matrix_rndm_order_vector = new int [matrix_size];
  else if (aux_isinteger==1) matrix_rndm_columns_int = new int [matrix_size];
  else if (aux_isinteger==0) matrix_rndm_columns= new double [matrix_size];

  // Also we dimension and initialize the aux_counters, used to send/recieve results of each slave cpu 
  aux_counter_adjusted = new unsigned long int[aux_num_rows];
  aux_counter_unadjusted = new unsigned long int[aux_num_rows];
  sum_counter_adjusted = new unsigned long int[aux_num_rows];
  sum_counter_unadjusted = new unsigned long int[aux_num_rows];
  for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) aux_counter_adjusted[i_loop]  =(unsigned long int)0; 
  for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) aux_counter_unadjusted[i_loop]=(unsigned long int)0; 
  for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) sum_counter_adjusted[i_loop]  =(unsigned long int)0; 
  for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) sum_counter_unadjusted[i_loop]=(unsigned long int)0; 

//********************************************** MAIN DATA DISTRIBUTION END ***************************************



  // some checks
  if (test_type == "t") {
        if (val_columns_int.max() != 1) {
      cout << "ERROR: for t there should be two different classes" << endl;
      cout << "In your data, there are " << val_columns_int.max() + 1 <<
	" distinct classes." << endl;
      exit(1);
    }
  }



/**************************************************************
 *****                                                   ******
 *****         Some variables we need etc                ******
 *****                                                   ******
 **************************************************************/
  valarray<double> observed_test_statistic(aux_num_rows);
  valarray<double> ordered_observed_test_statistic(aux_num_rows);
  valarray<unsigned int> order_stat_decreasing(aux_num_rows);
  valarray<unsigned long int> counter_adjusted_p_value(aux_num_rows);
  valarray<unsigned long int> counter_unadjusted_p_value(aux_num_rows);
  valarray<double> adjusted_p_value(aux_num_rows);
  valarray<double> unadjusted_p_value(aux_num_rows);
  valarray<double> FDR_indep_p_values(aux_num_rows);
  valarray<double> FDR_dep_p_values(aux_num_rows);

  // Next only needed when test = Cox
  valarray<int> order_vector(aux_num_columns);
  for(unsigned int i = 0; i < aux_num_columns; i++) order_vector[i] = i;

/**************************************************************
**************                                    *************
**************        Observed statistics         *************
**************                                    *************
***************************************************************/

  if(test_type == "Cox") {
    // Need to: a) center covariates; b) order data according to survival time
    // Covariate centering doexºs not need to be done again.

    all_covariates_centering(val_covariates, val_missing, 
			     aux_num_columns, aux_num_rows);
    sort_for_survival(aux_num_columns, aux_num_rows, 
		      aux_length_data,
		      val_columns,
		      val_censored_status, 
		      val_covariates, val_missing);
    // recall that datos.columns holds the survival times
  }

  if(test_type == "Regres") //make life easier
    all_covariates_centering(val_covariates, val_missing,
			     aux_num_columns, aux_num_rows);


  int number_of_run = 0;

  compute_test_statistic(aux_length_data,
			 aux_num_columns,
			 aux_num_rows,
			 val_missing,
			 val_covariates,
			 val_columns,
			 val_columns_int,
			 val_censored_status,
			 observed_test_statistic,
			 test_type,
			 number_of_run);

//   if(minP == "minP") 
//     for(unsigned int i = 0; i < datos.num_rows; ++i) {
//       minPstats.write(reinterpret_cast<const char *>(& observed_test_statistic[i]),
// 		      sizeof( observed_test_statistic[i] ));
//     }


  //xx: DEBUG
   // if we use minP (without Fisher case) we don't order statistics here,
   // but at the end
   if(minP != "minP") order_observed_statistics(order_stat_decreasing,
						ordered_observed_test_statistic,
						observed_test_statistic,
						aux_num_rows);



// MASTER loops over slaves and for each one fills a matrix with columns that represent the randomly shuffled lable array and sends it.
// Unless test is FisherIxJ 
if ((rank==0)&&(test_type!="FisherIxJ"))
{
	// Initialize seed
	gsl_rng * r = gsl_rng_alloc(gsl_rng_mt19937);
	gsl_rng_set(r, seed_r);

	//Loop over slaves and send each one a different matrix 
	for (cpu_loop=1;cpu_loop<numberOFcpu;cpu_loop++){
		for (row_loop=0;row_loop<matrix_numrows;row_loop++){

			if (test_type == "Cox"){
				random_shuffle_3(&order_vector[0],
						 &order_vector[order_vector.size()], r);
	
				for (col_loop=0;col_loop<aux_num_columns;col_loop++){
					matrix_position = row_loop * aux_num_columns + col_loop;
					matrix_rndm_order_vector[matrix_position] = order_vector[col_loop];
				}

			}
			else if (aux_isinteger==1) {	
				random_shuffle_3(&val_columns_int[0],
						 &val_columns_int[val_columns_int.size()], r);
	
				for (col_loop=0;col_loop<aux_num_columns;col_loop++){
					matrix_position = row_loop * aux_num_columns + col_loop;
					matrix_rndm_columns_int[matrix_position] = val_columns_int[col_loop];
				}
			}
			else if (aux_isinteger==0) {
				random_shuffle_3(&val_columns[0],
						 &val_columns[val_columns.size()], r);
	
				for (col_loop=0;col_loop<aux_num_columns;col_loop++){
					matrix_position = row_loop * aux_num_columns + col_loop;
					matrix_rndm_columns[matrix_position] = val_columns[col_loop];
				}
			}
		}

		//Send appropriate matrix
		if (test_type == "Cox")    MPI::COMM_WORLD.Send(matrix_rndm_order_vector, matrix_size, MPI::INT, cpu_loop, 0);
		else if (aux_isinteger==1) MPI::COMM_WORLD.Send(matrix_rndm_columns_int, matrix_size, MPI::INT, cpu_loop, 1);
		else if (aux_isinteger==0) MPI::COMM_WORLD.Send(matrix_rndm_columns, matrix_size, MPI::DOUBLE, cpu_loop, 2);
		
	}
	gsl_rng_free(r);

}

// Each slave recieves the matrix and process it
if ( (rank!=0) && (test_type!="FisherIxJ") )
{	
		//recieve appropriate matrix
		if (test_type == "Cox")    MPI::COMM_WORLD.Recv(matrix_rndm_order_vector, matrix_size, MPI::INT, 0, 0);
		else if (aux_isinteger==1) MPI::COMM_WORLD.Recv(matrix_rndm_columns_int, matrix_size, MPI::INT, 0, 1);
		else if (aux_isinteger==0) MPI::COMM_WORLD.Recv(matrix_rndm_columns, matrix_size, MPI::DOUBLE, 0, 2);
	
	/**************************************************************
	
	**************                                    *************
	**************      Permuted statistics           *************
	**************                                    *************
	***************************************************************/
	
	
	/**************************************************************
		Stuff related to the random number generator.
		For details, see ch. 19 GSL docs.
	***************************************************************/
	// Las primeras líneas las usaríamos si quisieramos controlar
	// el tipo de generador y su semilla desde línea de comandos.
	// Por sencillez, fijo el generador en el Mersenne Twister, y la seed 
	// la saco del time.
	// const gsl_rng_type * T;
	// gsl_rng * r;
	// gsl_rng_env_setup();
	// T = gsl_rng_default;
	// r = gsl_rng_alloc (T);
	//   gsl_rng * r = gsl_rng_alloc(gsl_rng_mt19937);
	//    unsigned long int seed_r = time(0);
	//   gsl_rng_set(r, seed_r);
	
	//  Do the permutation (random or systematic)
	
	//  For now, only random because the code for systematic
	//  is not general enough for more than 2 classes and
	//  for continuous covariates-
	//  if(num_permut) { // if random permutation:
	
	
	valarray<double> permuted_test_statistic(aux_num_rows);
	//int index_minP = datos.num_rows; //only used if minP
	
	//Slave loops over rows of the random matrix
	for (unsigned int B = 0; B < matrix_numrows; B++) {
	
		// Depending on the test type fill appropriate valarry with matrix row
		if (test_type == "Cox"){
			for (col_loop=0; col_loop < aux_num_columns ;col_loop++){
				matrix_position           = B * aux_num_columns + col_loop;
				order_vector[col_loop]    = matrix_rndm_order_vector[matrix_position];
			}
			permute_covars(val_covariates, val_missing, order_vector,aux_num_rows, aux_num_columns);
		}
		else if (aux_isinteger==1){
			for (col_loop=0; col_loop < aux_num_columns ;col_loop++){
				matrix_position           = B * aux_num_columns + col_loop;
				val_columns_int[col_loop] = matrix_rndm_columns_int[matrix_position];
			}
		}
		else if (aux_isinteger==0){
			for (col_loop=0; col_loop < aux_num_columns ;col_loop++){
				matrix_position           = B * aux_num_columns + col_loop;
				val_columns[col_loop]     = matrix_rndm_columns[matrix_position];
			}
		}
	
			compute_test_statistic(aux_length_data,
						aux_num_columns,
						aux_num_rows,
						val_missing,
						val_covariates,
						val_columns,
						val_columns_int,
						val_censored_status,
						permuted_test_statistic,
						test_type,
						B+1);
		
		if((minP != "minP") && (test_type != "Fisher") && 
			(test_type != "FisherIxJ")) //unadjusted p only if not minP
		increase_unadjusted_p_value_counter(counter_unadjusted_p_value,
							permuted_test_statistic, 
							ordered_observed_test_statistic,
							order_stat_decreasing, 
							aux_num_rows);
	// 	if(minP != "minP") increase_adjusted_p_value_counter(counter_adjusted_p_value, 
	// 								permuted_test_statistic,
	// 								ordered_observed_test_statistic, 
	// 								order_stat_decreasing,
	// 								aux_num_rows);
	
	} //B: end loop over random permutations
	
	// Transform valarrays to normal arrays to be able to send them
	//for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) aux_counter_adjusted[i_loop]  =counter_adjusted_p_value[i_loop]; 
	for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) aux_counter_unadjusted[i_loop]=counter_unadjusted_p_value[i_loop]; 

 }


// Each node sends their aux_counter and master recieves and adds them up (i.e. mpi reduce) at sum_counter
//MPI::COMM_WORLD.Reduce(aux_counter_adjusted, sum_counter_adjusted, aux_num_rows, MPI::UNSIGNED_LONG, MPI::SUM, 0);
if (test_type!="FisherIxJ") MPI::COMM_WORLD.Reduce(aux_counter_unadjusted, sum_counter_unadjusted, aux_num_rows, MPI::UNSIGNED_LONG, MPI::SUM, 0);

// MASTER transforms normal arrays to valarrays, calculates necessary parameters and prints results to result file.
 if (rank==0)
 {

	// Transform normal arrays to valarrays to be able to continue serial code
	//for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) counter_adjusted_p_value[i_loop]=sum_counter_adjusted[i_loop]; 
	if (test_type!="FisherIxJ") for ( i_loop=0 ; i_loop<aux_num_rows ; i_loop++ ) counter_unadjusted_p_value[i_loop]=sum_counter_unadjusted[i_loop]; 
	
	
	if(minP != "minP") {
		for(unsigned int i = 0; i < aux_num_rows; i++) {
		// 	adjusted_p_value[i] = 
		// 	 static_cast<double>(counter_adjusted_p_value[i])/num_permut;
		
			if(test_type != "FisherIxJ") 
				unadjusted_p_value[i] = 
				static_cast<double>(counter_unadjusted_p_value[i]+1)/(num_permut+1);
		}
		
		if((test_type == "Fisher") || (test_type == "FisherIxJ")) {
		// For FDR to work, we need to make "unadjeusted_p_value" = 
			// exact_p_value, but ordered
			for(unsigned int i = 0; i < aux_num_rows; i++)
				unadjusted_p_value[i] = 
				1 - observed_test_statistic[order_stat_decreasing[i]];
		}
	}
	
	// ****************** Ensure monotonicity constraints *********************
	
	//    for(unsigned int i = 1; i < aux_num_rows; i++) {
	//      adjusted_p_value[i] = max(adjusted_p_value[i], adjusted_p_value[(i-1)]);
	//    }
	
	
	// *****************  FDR   **********************************************
	FDR_p_value(FDR_indep_p_values, FDR_dep_p_values, unadjusted_p_value, 
		aux_num_rows, order_stat_decreasing); 
	
	
	ofstream results_out(s2.data());
	
	// For output, need to find out length of largest string
	size_t max_size_string_ID = 0;
	for(unsigned int i = 0; i < aux_num_rows; ++i) {
		max_size_string_ID = max(max_size_string_ID, aux_ID[i].length());
	}
	size_t num_spaces;
	// this is awkward, but how else can I prevent getting an unsigned int 
	// to be subst. a larger number?
	if (max_size_string_ID + 5 > 12) num_spaces = max_size_string_ID + 5;
	else num_spaces = 12;
	string blank_spaces(num_spaces - 2, ' ');
	
	
	results_out <<" Function call:                  \t";
	for(int n = 0; n < argc; ++n) results_out << argv[n] << " ";
	results_out << "\n Data file:                   \t\t" << argv[4];
	results_out << "\n Class file:                  \t\t" << argv[5];
	results_out << "\n Number of variables or genes:\t\t" << aux_num_rows;
	results_out << "\n Number of columns:           \t\t" << aux_num_columns;
	results_out << "\n Type of test:                \t\t" << test_type;
	results_out << "\n MinP or MaxT?:               \t\t" << minP;
	results_out << "\n Permutations used:           \t\t" ;
	if (test_type == "FisherIxJ") {
	  results_out << "Non permutation method";
	} else {
	  results_out << num_permut;
	}
	results_out << "\n Random seed:                 \t\t" << seed_r;
	results_out << "\n\n";
	results_out.setf(ios::right);
	results_out << 
	"###############################################################\n\n\n";
// 	results_out.width(8); 
	results_out << "Row\t";
// 	for (unsigned int j = 0; j < num_spaces - 2; ++ j) results_out << " "; 
// 	results_out.width(2); 
	results_out << "ID\t";
	//    results_out << "       unadj.p       adj_p         FDR_indep"
	// 	       <<"       FDR_dep         obs_stat         abs(obs_stat)";
	results_out << "unadj.p\tFDR_indep"
		<<"\tobs_stat\tabs(obs_stat)";
	results_out << endl;
	
	for (unsigned int i = 0; i < aux_num_rows; i++) {
	  results_out << order_stat_decreasing[i] + 1 << "\t";
	  results_out << aux_ID[ order_stat_decreasing[i] ]<< "\t";
	  results_out.width(30);
	  cout <<  unadjusted_p_value[i] << "\t";
	  results_out.width(30); results_out.precision(26);	  
	  cout <<  FDR_indep_p_values[i] << "\n";
	  results_out.width(30); results_out.precision(26);	  
	  results_out << unadjusted_p_value[i] << "\t";
	  results_out.width(30); results_out.precision(26);	  
	  cout << unadjusted_p_value[i] << "\t";
	  results_out.width(30); results_out.precision(26);	  
	  results_out << FDR_indep_p_values[i] << "\t";
	  results_out.width(30); results_out.precision(26);	  
	  cout << FDR_indep_p_values[i] << "\n";
	  results_out.width(30); results_out.precision(26);	  
	  results_out << observed_test_statistic[ order_stat_decreasing[i] ] << "\t";
	  results_out.width(30); results_out.precision(26);	  
	  if(test_type != "FisherIxJ") results_out <<  ordered_observed_test_statistic[i] <<endl;
	  else results_out <<  observed_test_statistic[ order_stat_decreasing[i] ] << endl;
	}
	
	
	
	cout << s2 << endl;
	results_out.close();

}
   MPI::Finalize();
	return 0;


}



