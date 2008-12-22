/***************************************************************************
    readMissing.cpp: utilities for reading the data, allowing for missing.
***************************************************************************/ 




/***************************************************************************
    begin                : Thu Jul 11 19:21:37 CEST 2002
    copyright            : (C) 2002-2009  by 
                            Ramón Díaz-Uriarte
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





#include"readMissing.h"

#include<iostream>
#include<vector>
#include<string>
#include<fstream>
#include<map>


using namespace std;
// #define PR(x) cout << #x " = " << x << endl;
#define PR(x);


void update_data_and_missing(const string &tmp_string, vector<double> &data,
     vector<int> &missing, unsigned int &num_columns) {
// pass it a string, with the possible value, and 
// updates the data vector and the missing value vector.
// I hard code here that missing values are "NA" and " ".
// We skip lines that start with "#"
    // The two missing value codes are: NA and " " (i.e., an empty space).
  if((tmp_string =="") || (tmp_string == " ") || (tmp_string == "NA") ||
     (tmp_string =="\r") || (tmp_string == "\f") ||
     (tmp_string ==" \r") || (tmp_string == "NA\r") ||
     (tmp_string ==" \f") || (tmp_string == "NA\f") ||
     (tmp_string =="\n") || (tmp_string == " \n") || (tmp_string == "NA\n")){
    //the last line shouldn't be necessary, but just in case
    //    cout << "       Considering it missing " << endl;
    data.push_back(-939393.9393);
    missing.push_back(1);
    ++num_columns;
  }
  else {
    //  cout << " Considering it valid with value "<<atof(tmp_string.data())
    //       <<   endl;
    data.push_back(atof(tmp_string.data()));
    missing.push_back(0);
    ++num_columns;
  }
}


int read_data(vector<double> &data, vector<int> &missing, vector<string> &ID, 
	      ifstream &data_stream, unsigned int &num_rows, 
	      unsigned int &num_columns) {

  // Leer las cosas separadas por "\t" (por consistencia con SOTA).
  // si encuentro un " " o un "" o un "NA" eso es missing.
  // The first column is an identifier (always.)

  string tmpInput;
  string tmp_data_value;
  num_columns = num_rows = 0;
  unsigned int previous_num_columns = 0;
  previous_num_columns = num_columns;
  std::string::size_type location_first_tab; //see Jousttis, p. 495 
                                     // for warnings on use of npos.

  while(getline(data_stream, tmpInput)) {
    if((tmpInput.length()) && (tmpInput[0] != '#')) { //only use lines that do not start with "#".
                  // and also eliminate those that have only a carriage return
      ++num_rows;
      location_first_tab = 0;
      num_columns = 0;

      // Get the ID, which is whatever there is before the first tab
      string tmp_ID;
      location_first_tab = tmpInput.find('\t');
      tmp_ID = tmpInput.substr(0, location_first_tab);
      ID.push_back(tmp_ID);
      tmpInput.erase(0, (location_first_tab + 1));

      // get the rest of the data
      while(location_first_tab != std::string::npos) {
	location_first_tab = tmpInput.find('\t');
	if(location_first_tab != std::string::npos) {
	  tmp_data_value = tmpInput.substr(0, location_first_tab);
	  update_data_and_missing(tmp_data_value, data, missing, num_columns);
	  tmpInput.erase(0, (location_first_tab + 1));
  
	}
	else { // i.e., last tab
	  tmp_data_value = tmpInput;
	  PR(tmp_data_value);
	  update_data_and_missing(tmp_data_value, data, missing, num_columns);
	}
      }
     
      PR(num_columns);
      PR(previous_num_columns);
      if((num_rows - 1) && (num_columns != previous_num_columns)) {
	cout << "ERROR: different number of columns at row " << num_rows <<";\n" 
	     << "the previous rows had " << previous_num_columns << " columns;\n"
	     << "this row has " << num_columns << " columns." << endl;
	exit(1);
      }
      previous_num_columns = num_columns;
    }
  }
  return 0;
}


input_data_struct::input_data_struct(std::ifstream &data_stream,
				     std::ifstream &class_stream,
				     std::ifstream &censored_stream,
				     std::string &test_type) {
  // Note that the code almost always calls this one,
  // because it can also deal with cases when there
  // is no censored_stream.


  // First, read the data, using read_data.
  std::vector<double> data_vec;
  std::vector<int> missing_vec;
  std::vector<double> classlabels_vec;
  std::vector<int> classlabels_vec_int;
  std::vector<int> censored_vec;
  unsigned int n_cols = 0;
  unsigned int n_rows = 0;

  bool survival_data = false;
  if(censored_stream) survival_data = true;
  char tmp[80];
  read_data(data_vec, missing_vec, ID, data_stream, n_rows, n_cols);
  if(survival_data) while(censored_stream >> tmp) 
    censored_vec.push_back(atoi(tmp));

  if((test_type != "Fisher") && (test_type != "FisherIxJ") 
     && (test_type != "contin")
     && (test_type != "Anova") && (test_type != "t")) {
    while(class_stream >> tmp) classlabels_vec.push_back(atof(tmp));
    if(classlabels_vec.size() != n_cols) {
      std::cout << "error ERROR: different number of class labels (" 
		<< classlabels_vec.size() <<") and columns of data (" << n_cols <<")" 
		<< std::endl;
      exit(1);
    }
  }

  else { //convert arbitrary categorical coding to ints starting at 0.
    vector<string> categorical_labels;
    map<string, int> labels_map;

    while(class_stream >> tmp) categorical_labels.push_back(tmp);
    if(categorical_labels.size() != n_cols) {
      std::cout << "error ERROR: different number of class labels (" 
		<< categorical_labels.size() <<") and columns of data (" << n_cols <<")" 
		<< std::endl;
      exit(1);
    }

    classlabels_vec_int.resize(categorical_labels.size());
    int insertion_occasion = 1;
    
    for (unsigned int i = 0; i < categorical_labels.size(); ++i) {
      if (labels_map[ categorical_labels[i] ]== 0) {
	labels_map[ categorical_labels[i] ] = insertion_occasion;
	++ insertion_occasion;
      }
     classlabels_vec_int[i] = labels_map[categorical_labels[i]] - 1;
    }
  }

  data_stream.close();
  class_stream.close();
  if(survival_data) censored_stream.close();


  if(survival_data && (censored_vec.size() != n_cols)) {
           std::cout << "error ERROR: different number of censored data ("
		     << censored_vec.size() 
		     <<") and columns of data (" << n_cols <<")" << std::endl;
    exit(1);
  }

  // Now place things in the structure.
  // This follows the constructor scheme above.
  num_columns = n_cols;
  num_rows = n_rows;
  length_data = num_columns * num_rows;

  missing.resize(length_data);
  covariates.resize(length_data);
  if(survival_data) censored_status.resize(num_columns);

  if((test_type != "Fisher") && (test_type != "FisherIxJ") 
     && (test_type != "contin")
     && (test_type != "Anova") && (test_type != "t")) 
    columns.resize(num_columns);
  else
    columns_int.resize(num_columns);


  for(unsigned int i = 0; i < length_data; ++i) {
    missing[i] =  missing_vec[i];
    covariates[i] = data_vec[i];
  }

  for(unsigned int i = 0; i < num_columns; ++i) 
    if(survival_data) censored_status[i] = censored_vec[i];
  

  if((test_type != "Fisher") && (test_type != "FisherIxJ") 
     && (test_type != "contin")
     && (test_type != "Anova") && (test_type != "t")) 
    for(unsigned int i = 0; i < num_columns; ++i) 
      columns[i] = classlabels_vec[i];
  

  else 
    for(unsigned int i = 0; i < num_columns; ++i) 
	  columns_int[i] = classlabels_vec_int[i];

  data_vec.clear();
  missing_vec.clear();
  classlabels_vec.clear();
  classlabels_vec_int.clear();
  if(survival_data) censored_vec.clear();
}


// input_data_struct::input_data_struct(std::ifstream &data_stream,
// 				     std::ifstream &class_stream,
// 				     std::string &test_type) {
//   // The function that accepts also a censored_stream is
//   // slightly more general and thus is the one used by default.
//   // This left here just in case.

//   // First, read the data, using read_data.
//   std::vector<double> data_vec;
//   std::vector<int> missing_vec;
//   std::vector<double> classlabels_vec;
//   unsigned int n_cols = 0;
//   unsigned int n_rows = 0;

//   char tmp[80];
//   read_data(data_vec, missing_vec, ID, data_stream, n_rows, n_cols);
//   while(class_stream >> tmp) classlabels_vec.push_back(atof(tmp));

//   data_stream.close();
//   class_stream.close();

//   if(classlabels_vec.size() != n_cols) {
//     std::cout << "error ERROR: different number of data values and columns" 
//               << std::endl;
//     exit(1);
//   }

//   // Now place things in the structure.
//   // This follows the constructor scheme above.
//   num_columns = n_cols;
//   num_rows = n_rows;
//   length_data = num_columns * num_rows;

//   missing.resize(length_data);
//   covariates.resize(length_data);
//   columns.resize(num_columns);

//  for(unsigned int i = 0; i < length_data; ++i) {
//     missing[i] =  missing_vec[i];
//     covariates[i] = data_vec[i];
//   }

//   for(unsigned int i = 0; i < num_columns; ++i) {
//     columns[i] = classlabels_vec[i];
//   }

//   data_vec.clear();
//   missing_vec.clear();
//   classlabels_vec.clear();
// }


/* The following two are no longer used, but I leave them here
   just in case. Note that now we can read passing directly the
   input stream with the data with the other two functions.   */

// input_data_struct::input_data_struct(unsigned int number_rows,
//                        unsigned int number_columns,
//                           std::vector<double> columns_vec,
//                           std::vector<double> covariates_vec,
//                           std::vector<int>missing_vec){
//     num_columns = number_columns;
//     num_rows = number_rows;
//     length_data = num_columns * num_rows;

//     missing.resize(length_data);
//     covariates.resize(length_data);
//     columns.resize(num_columns);

//     for(unsigned int i = 0; i < length_data; ++i) {
//       missing[i] =  missing_vec[i];
//       covariates[i] = covariates_vec[i];
//     }
//     for(unsigned int i = 0; i < num_columns; ++i) {
//       columns[i] = columns_vec[i];
//     }
// }

// input_data_struct::input_data_struct(unsigned int number_rows,
//                   unsigned int number_columns,
//                      std::vector<double> columns_vec,
//                      std::vector<double> covariates_vec,
//                      std::vector<int>missing_vec,
//                      std::vector<int>censored_vec) {
//    num_columns = number_columns;
//    num_rows = number_rows;
//    length_data = num_columns * num_rows;

//    missing.resize(length_data);
//    covariates.resize(length_data);
//    columns.resize(num_columns);
//    censored_status.resize(num_columns);

//    for(unsigned int i = 0; i < length_data; ++i) {
//      missing[i] =  missing_vec[i];
//      covariates[i] = covariates_vec[i];
//    }
//    for(unsigned int i = 0; i < num_columns; ++i) {
//      columns[i] = columns_vec[i];
//      censored_status[i] = censored_vec[i];
//    }
// }





//*********  EXAMPLE OF USE **************
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
