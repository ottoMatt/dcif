/************************************************************************
 Copyright 2003-2009, University of Yamanashi. All rights reserved. 
 By using this software the USER indicates that he or she has read,
 understood and will comply with the following:

 --- University of Yamanashi hereby grants USER non-exclusive permission
 to use, copy and/or modify this software for internal, non-commercial,
 research purposes only. Any distribution, including commercial sale or
 license, of this software, copies of the software, its associated
 documentation and/or modifications of either is strictly prohibited
 without the prior consent of University of Yamanashi. Title to
 copyright to this software and its associated documentation shall at
 all times remain with University of Yamanashi.  Appropriate copyright
 notice shall be placed on all software copies, and a complete copy of
 this notice shall be included in all copies of the associated
 documentation. No right is granted to use in advertising, publicity or
 otherwise any trademark, service mark, or the name of University of
 Yamanashi.

 --- This software and any associated documentation is provided "as is"

 UNIVERSITY OF YAMANASHI MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS
 OR IMPLIED, INCLUDING THOSE OF MERCHANTABILITY OR FITNESS FOR A
 PARTICULAR PURPOSE, OR THAT USE OF THE SOFTWARE, MODIFICATIONS, OR
 ASSOCIATED DOCUMENTATION WILL NOT INFRINGE ANY PATENTS, COPYRIGHTS,
 TRADEMARKS OR OTHER INTELLECTUAL PROPERTY RIGHTS OF A THIRD PARTY.

 University of Yamanashi shall not be liable under any circumstances for
 any direct, indirect, special, incidental, or consequential damages
 with respect to any claim by USER or any third party on account of or
 arising from the use, or inability to use, this software or its
 associated documentation, even if University of Yamanashi has been
 advised of the possibility of those damages.
************************************************************************/

package org.nabelab.solar;

// MEMO for J2SE1.6
//import java.util.Arrays;

/**
 * @author nabesima
 *
 */
public class VarRenameMap {

  /**
   * Registers the variable and returns the renamed variable.
   * @param var the original variable.
   * @return the renamed variable.
   */
  public int put(int var) {
  
    for (int i=0; i < size; i++)
      if (map[i] == var)
        return i + offset;
  
    if (size == map.length) {
      // MEMO for J2SE1.6
      //map = Arrays.copyOf(map, size << 1);
      int[] oldMap = map;
      map = new int[size << 1];
      System.arraycopy(oldMap, 0, map, 0, oldMap.length);
    }
    
    int newvar = size;
    map[size++] = var;
    
    return newvar + offset;
  }

  /** 
   * Returns the maximum variable number.
   * @return the maximum variable number.
   */
  public int getMaxVar() {
    return size + offset - 1;
  }
  
  /**
   * Returns the number of kinds of variables in this map.
   * @return the number of kinds of variables in this map.
   */
  public int getNumVars() {
    return size;
  }
  
  /**
   * Sets the offset value of the first variable.
   * @param offset  the offset value.
   */
  public void setOffset(int offset) {
    this.offset = offset;
  }
  
  /**
   * Clears this variable rename mapping.
   */
  public void clear() {
    size = 0;
    offset = 0;
  }
  
  /** The initial size of the map. */
  private final static int INITIAL_SIZE = 8;
  
  /** The mapping from original variables to renamed variables. */
  private int[] map = new int[INITIAL_SIZE];
  /** The number of registered variables. */
  private int size = 0;
  /** The offset value of the first variable. */
  private int offset = 0;

}
