// Mr. Arkiletian ICTP 12
// Simultaneous linear equation assignment (2 team members)
// Solved using the STL generic vector container class 


#include <iostream>
#include <vector>
#include <cmath> // for pow function

using namespace std;

typedef vector <double> Dvector;
typedef vector <Dvector> Dmatrix;

// Prototypes (variable names included, but not needed)
// DO NOT change any prototypes!! NO other functions allowed.

Dmatrix GetA(); //done
// gets the matrix A from the user and returns it

Dvector Getb(const int &siz); //done
// gets the vector b from the user and returns it

void Display(const Dvector &xvect); //done
// displays the contents of vector xvect

void Display(const Dmatrix &Amat); //done
// displays the contents of matrix Amat (Note: Display function is overloaded)

Dvector Solvex(const Dmatrix &Amat, const Dvector &bvect); //done
// Solves for systems of linear equations in the form Ax=b using cramer's rule 

double Det(const Dmatrix &Amat);
// returns the Determinant of matrix Amat using a recursive algorithm
// base case is 2x2 matrix 

Dmatrix Replace(Dmatrix Rmat, const int col, const Dvector &bvect);
// Replaces the column 'col' in Rmat with bvect and returns Rmat

Dmatrix Minor(const Dmatrix &Amat, const int col);
// Gets the Minor matrix of Amat by crossing out the first row and 
// column 'col' then returns that smaller matrix


//-------------------------------------------
int main()
{

    Dmatrix A;     
    Dvector b,x;

    A=GetA();
    
    Display(A);
    
    b=Getb(A.size());
    Display(b);
    x=Solvex(A,b);
    Display(x);
    
    return(0);
}
//-------------------------------------------

Dmatrix GetA()
{
    unsigned int rows;
    double a;
    Dvector tempvec;
    Dmatrix tempmat;
    cin >> rows;
    for (long unsigned int i = 0; i < rows; i++) {
        
        
        for (long unsigned int n = 0; n < rows; n++) {
            
            cin >> a;
            tempvec.push_back(a);
        }
        
        tempmat.push_back(tempvec);
        tempvec.clear();
    }
        
    return tempmat;
}

void Display(const Dmatrix &Amat)
{
    for (long unsigned int i = 0; i < Amat.size(); i++) {
        for (long unsigned int x = 0; x < Amat[0].size(); x++) {
            cout << Amat[i][x] << " ";
            
        }
        
        cout << "\n";
        
    }
    
}

Dvector Getb(const int &siz)
{
    Dvector tempvec;
    double a;
    
    
    for (int i = 0; i < siz; i++) {
        
        cin >> a;
        tempvec.push_back(a);
    }
    
    return tempvec;
}

void Display(const Dvector &xvect)
{
    for (long unsigned int i = 0; i < xvect.size(); i++) {
        cout << xvect[i] << " ";
        
    }
    
    cout << "\n";
    
}

Dvector Solvex(const Dmatrix &Amat, const Dvector &bvect)
{
    Dmatrix matx;
    Dvector solutions;
    double deno = Det(Amat);
    
    for (int i = 0; i < bvect.size(); i++) {
        
        matx = Replace(Amat, i, bvect);
        sol = Det(matx)/deno;
        solutions.push_back(sol);
    }
    
    
    return solutions;
    
}

double Det(const Dmatrix &Amat)
{
    
    if (Amat.size() == 2) {
        return Amat[0][0]*Amat[1][1]-Amat[0][1]*Amat[1][0];
        
    }
    
    for (int c = 0; c < Amat.size(); i++) {
        
        return pow(-1, c)*Amat[0][c]*Det(Minor(Amat, c);
        
    }
    
    
    
}
    
Dmatrix Minor(const Dmatrix &Amat, const int col)
{
    Dmatrix minmat;
    Dvector tempvec;
    

    for (long unsigned int i = 1; i <= Amat.size(); i++) {
        
        
        for (long unsigned int n = 0; n < Amat.size(); n++) {
            
            if (n != col) {
                tempvec.push_back(Amat[i][n]);
            }
        }
        
        minmat.push_back(tempvec);
        tempvec.clear();
    }
        
    return minmat;
    
}

Dmatrix Replace(Dmatrix Rmat, const int col, const Dvector &bvect)
{
    int n = 0;
    
    for (int row = 0; row < int(Rmat.size()); row++) {
        Rmat[row][col] = bvect[n];
        n++;
    }
    
    return Rmat;
    
}

