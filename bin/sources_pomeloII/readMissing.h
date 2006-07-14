/***************************************************************************
                          readMissing.h  -  description
                             -------------------
    begin                : Tue Jul 16 2002
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
// Code to read data and deal with missing values.
// Use the read_data function; pass it: the vector where you
// want the data, the vector where you want the missing stuff,
// the input stream (the file) and the variables were number
// or rows and columns will be stored.
// read_data returns an int, just to be able to "return 1;" if
// errors. Wil fix and use exceptions later.
//
//
// Now the file format is:
//   - Tab separated
//   - Missing with NA, " ", "".
//   - First column is the ID-

// For ease of use, I have prepared a set of constructors that
// read the data directly into the input_data_struc. For the
// usual cases, pass it the ifstreams, as in
//   input_data_struct datos(data_stream, class_stream, censored_stream);
// it is OK if there is no censored_stream.

// See examples of use at end.


#ifndef GUARD_readMissing
#define GUARD_readMissing

#include<iostream>
#include<valarray>
#include<vector>
#include<string>
#include<fstream>


int read_data(std::vector<double> &data, std::vector<int> &missing,
	      std::vector<std::string> &ID, std::ifstream &data_stream, 
	      unsigned int &num_rows, unsigned int &num_columns);

void update_data_and_missing(const std::string &tmp_string,
                             std::vector<double> &data,
                             std::vector<int> &missing,
                             unsigned int &num_columns);


class input_data_struct {
  // The data are in the typical DNA array setup:
//     - rows are genes
//     - columns are classes of patients, or some other
//       dependent variable (e.g., survival).
//     - covariates are the covariates or genes expression,
//       or whatever. Can be discrete (Fisher test) or continuous
//       (other things).
//
//     - A table of cases:
//         The test in the box is the test used to examine if
//         if there are differences in gene expression (or whatever)
//         related to differences in the value of the column.
//
//
//                                 Response or Classif. var. (column)
//                               ________________________________
//                                Discr.    |  Cont.     | Surv.
//                             ||___________|____________|________
//                             ||           |            |
//                  Discrete   ||Fisher     |    XX      |  Cox regres.
//Covar. or gene.              ||___________|____________|________
//  expression                 ||           |            |
// (rows)           Continuous || Anova,    |  Linear    |  Cox regres.
//                             ||  t        | regression |
//
//                  XX: could use logistic regression or multinomial model.
//                      Not implemented now.

// This would be much nicer with virtual functions,
// but for now use a very general, encompassing container.

  // Everything is public for now. Don't feel like writing
  // many member functions. This is just a more elaborate structure.
  public:
     unsigned int length_data;
     unsigned int num_columns;
     unsigned int num_rows;
     std::valarray<int> missing;
     std::valarray<double> covariates;
     std::valarray<double> columns; //continuous data
     std::valarray<int> columns_int; //For t, anova, contin, Fisher, FisherIxJ
     std::valarray<int> censored_status;
     std::vector<std::string> ID;

// The following two are no longer used
/*      input_data_struct(unsigned int number_rows, */
/*                        unsigned int number_columns, */
/*                           std::vector<double> columns_vec, */
/*                           std::vector<double> covariates_vec, */
/*                           std::vector<int>missing_vec); */

/*      input_data_struct(unsigned int number_rows, */
/*                        unsigned int number_columns, */
/*                           std::vector<double> columns_vec, */
/*                           std::vector<double> covariates_vec, */
/*                           std::vector<int>missing_vec, */
/*                           std::vector<int>censored_vec); */

     input_data_struct(std::ifstream &data_stream,
		       std::ifstream &class_stream,
		       std::ifstream &censored_stream,
		       std::string &test_type);

/*      input_data_struct(std::ifstream &data_stream, */
/*                     std::ifstream &class_stream); */


}; //class input_data_struct



#endif



//*********  EXAMPLE OF USE OF read_data**************
//int main(int argc, char *argv[])
//{
//  vector<double> data;
//  vector<int> missing;
//  ifstream data_stream(argv[1]);
//  int num_columns, num_rows;
//  read_data(data, missing, data_stream, num_rows, num_columns);
//
//  // Put into valarrays
//   valarray<double> data_array(data.size());
//   valarray<bool> missing_array(data.size());
//
//      for (unsigned int i = 0; i < data.size(); ++i) {
//        data_array[i] = data[i];
//        missing_array[i] = missing[i];
//      }
//
//   cout <<"\n********* VALUES ************\n";
//   for (int i = 0; i < (num_rows * num_columns); ++i) {
//     if((i % num_columns) == 0) {
//       cout << endl;
//       cout << data_array[i] << " ";
//     }
//     else cout << data_array[i] << " ";
//   }
//   cout << endl << endl << endl;
//
//   cout <<"\n********* MISSING ************\n";
//   for (int i = 0; i < (num_rows * num_columns); ++i) {
//     if((i % num_columns) == 0) {
//       cout << endl;
//       cout << missing_array[i] << " ";
//     }
//     else cout << missing_array[i] << " ";
//   }
//   cout << endl << endl << endl;
//
//  return 0;
//}


//*********  EXAMPLE OF USE OF input_data_struct**************
//#include"readMissing.h"
//using namespace std;
//
//int main(int argc, char *argv[])
//{
//
//
//  if((argc != 6) && (argc != 5)) {
//     cout <<"\n USAGE:";
//     cout <<"\n multest nperm test covariate_data class_data [censored_data]\n";
//     cout <<"\n   nperm: number of permutations\n\n";
//     cout <<"\n   test:  type of test; one of:";
//     cout <<"\n          Fisher:    minP with Fisher's exact test;";
//     cout <<"\n          contin:    maxT contingency table (not recommended)";
//     cout <<"\n          t:         maxT t-test (welch's);";
//     cout <<"\n          ANOVA:     maxT ANOVA;";
//     cout <<"\n          Cox:       maxT cox regression (survival analysis);";
//     cout <<"\n          Regres:    maxT linear regression;";
//     cout <<"\n          Regr2:     maxT quadratic regression;";
//     cout <<"\n          RegrLX:    maxT regression, log-transf. X;";
//     cout <<"\n          RegrLX:    maxT regression, log-transf. Y;";
//     cout <<"\n          RegrLXLY:  maxT regression, log-transf. X & Y;";
//     cout <<"\n\n";
//     cout <<"\n   covariate_data: rows are genes, columns are conditions.";
//     cout <<"\n   class_data:     classification variable or dep. var.";
//     cout <<"\n   [censored_data]: if survival data, the censoring indicator";
//     cout <<"\n \n \n" << endl;
//     return 1;
//     }
//
//  string test_type = argv[1];
//  int num_permut = atoi(argv[2]);
//  bool survival_data = false;
//  ifstream data_stream(argv[3]);
//  ifstream class_stream(argv[4]);
//  ifstream censored_stream(argv[5]);
//
//  if(argc == 6) {
//    survival_data = true;
//    }
//  else {
//    survival_data = false;
//  }
//
//  input_data_struct datos(data_stream, class_stream, censored_stream);
//
//
//    // Testeo:
//
//    cout << " \n Arguments \n";
//    for (int k = 0; k < argc; ++k) cout << argv[k] <<" ";
//    cout << " \n Datos " << endl;
//    int i = 0;
//    for (unsigned int j = 0; j < datos.num_rows; ++j) {
//           for(unsigned int k = 0; k < datos.num_columns; ++k) {
//               cout << datos.covariates[i] << " ";
//               ++i;
//           }
//           cout << endl;
//    }
//
//    cout << " \n columns \n ";
//    for (unsigned int l = 0; l < datos.num_columns; ++l) 
//                 cout << datos.columns[l] << " ";
//
//    if(argc == 6) {
//    cout << " \n censored status \n ";
//    for (unsigned int h = 0; h < datos.num_columns; ++h) 
//                          cout << datos.censored_status[h] << " ";
//    }
//    cout << "\n" << endl;
//
//    return 0;
//
//}


