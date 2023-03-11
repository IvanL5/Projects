import random
import sys
from time import process_time as timer
sys.setrecursionlimit(1000000000)

#Bubble Sort Algorithm

def bubbleSort(array):
    while(True):
        swapDetected = False
        for i in range(0, len(array)-1):
            if array[i] > array[i+1]:
                array[i], array[i+1] = array[i+1], array[i]
                swapDetected = True
        if not swapDetected:
            break

#Insertion Sort Algorithm

def insertionSort(array):
    for i in range(1,len(array)): 
        val, pos = array[i], i
        while pos>0 and array[pos-1]>val: 
            array[pos] = array[pos-1]
            pos = pos-1
        array[pos]=val

#Merge Sort Algorithm

def merge(dest, a1, a2):
    i, j, k = 0, 0, 0
    while i < len(a1) and j < len(a2):
        if a1[i] < a2[j]:
            dest[k]=a1[i]
            i=i+1
        else:
            dest[k]=a2[j]
            j=j+1
        k=k+1
    while i < len(a1):
        dest[k]=a1[i]
        i=i+1
        k=k+1
    while j < len(a2):
        dest[k]=a2[j]
        j=j+1
        k=k+1

def mergeSort(array):
    if len(array) <2:
        return
    mid = len(array) // 2
    left = array[:mid]
    right = array[mid:]
    mergeSort(left)
    mergeSort(right)
    merge(array, left, right)
    
#Finds Median
def med3(a,b,c):
    if a > b:
        if a < c: return a
        elif b > c: return b
        else: return c
    else:
        if a > c: return a
        elif b < c: return b
        else: return c

#QuickSort Algorithm

def partition(a, lo, hi):
    pivot = med3(a[lo],a[(lo+hi)//2],a[hi]) #Worst case and average case uses: pivot = a[lo], Best Case uses: pivot = med3(a[lo],a[(lo+hi)//2],a[hi])
    i, j = lo, hi
    while True:
        while a[i] < pivot: i = i + 1
        while a[j] > pivot: j = j - 1
        if i >= j: return j
        a[i], a[j] = a[j], a[i]
        i, j = i + 1, j - 1
 
def quicksortHelper(a, lo, hi):
    if lo >= hi: return
    p = partition(a, lo, hi)
    quicksortHelper(a, lo, p)
    quicksortHelper(a, p + 1, hi)
 
def quickSort(array):
	quicksortHelper(array, 0, len(array)-1)

#Sorting Algorithm Testing Function
def sortArray(size,order,algorithm,outputfile):
    check = str(size)
    if not check.isnumeric() or size < 0:
        print("Invalid input for size")
    check = str(outputfile)
    if not check.endswith(".txt"):
        print("Invalid output file name")
    array = [random.randint(1,1000000) for x in range(size)]
    global start
    global end
    if order == 'ascending':
        array.sort()
    elif order == 'descending':
        array.sort(reverse = True)
    elif order == 'random':
        pass
    else:
        print("Invalid input for order")
    if algorithm == 'bubble':
        start = timer()
        bubbleSort(array)
        end = timer()
        with open(outputfile,'w') as result:
            for i in array:
                result.write(str(i))
                result.write('\n')
            result.close
    elif algorithm == 'insertion':
        start = timer()
        insertionSort(array)
        end = timer()
        with open(outputfile,'w') as result:
            for i in array:
                result.write(str(i))
                result.write('\n')
            result.close
    elif algorithm == 'merge':
        start = timer()
        mergeSort(array)
        end = timer()
        with open(outputfile,'w') as result:
            for i in array:
                result.write(str(i))
                result.write('\n')
            result.close
    elif algorithm == 'quick':
        start = timer()
        quickSort(array)
        end = timer()
        with open(outputfile,'w') as result:
            for i in array:
                result.write(str(i))
                result.write('\n')
            result.close
    else:
        print("Invalid input for algorithm")
        return

#Example of SortArray function call
sortArray(1000,'random','bubble','bubblesort.txt')

#Print sorting time
print(end-start)
