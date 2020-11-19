# import sys
import os
import os.path as path
import shutil
import fnmatch as fm
import numpy as np
import pandas as pd
from scipy.io import loadmat
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QObject, pyqtSignal


class DataProcessor(QObject):
    print_out = pyqtSignal(str)
    prog_out = pyqtSignal(int)
    fin_out = pyqtSignal()
    prog = 0

    def __init__(self):
        QObject.__init__(self)
        self.__headDir = None
        self.__testDir = None
        self.interrupt = False

    def setPath(self, hd=None, td=None):
        self.__headDir = hd
        self.__testDir = td

    def printOut(self, strLine):
        self.print_out.emit(strLine)

    def progUpt(self, value):
        self.prog += value
        self.prog_out.emit(self.prog)

    def verifyExistDir(self, inDir):
        # Return the absolute path of inDir
        absPath = None

        if path.isdir(inDir):
            # Given path exists
            if path.isabs(inDir):
                absPath = inDir
                self.printOut('Test data directory %s already exists.' % absPath)
            else:
                absPath = path.abspath(inDir)
                self.printOut('Test data directory %s already exists.' % inDir)

        else:
            # Given path do not exist
            self.printOut('Directory %s do not exist.' % inDir)
            self.printOut('Please specify a valid directory for the test data.\n')

        return absPath

    def scaleTime_csvDat(self, f_dir):
        self.printOut('\nScaling the Time<ms> to Time<s> of the SMART Terminal Recorded Data.')

        # Read the file
        with open(f_dir, 'rb') as f:
            temp = f.readlines()

        with open(f_dir, 'wb') as f:
            for row in temp:
                if temp[0] == row:
                    f.write(row)
                else:
                    char = str(chr(row[0]))
                    if char.isdigit() and str(row).find(':') == 4:
                        f.write(row)

        # Open the file
        with open(f_dir, 'rb') as f:
            dat_df = pd.read_csv(f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)

        # Drop 'System Time' column
        # dat_df = dat_df.drop('System Time', 1)

        n_rows = dat_df.shape[0]
        n_cols = dat_df.shape[1]

        self.printOut('There are %d rows and %d columns of data in %s.' % (n_rows, n_cols, path.abspath(f_dir)))

        # Convert milliseconds to seconds
        dat_df['Time<ms>'] /= 1000.0000

        # Change column label
        dat_df = dat_df.rename(columns={'Time<ms>': 'Time<s>'})

        # Write to a file
        sf_dir = str(f_dir[:-4]) + '_SCALED.csv'
        dat_df.to_csv(sf_dir, index=False)

        self.printOut('Finished writing scaled data into %s.' % path.abspath(sf_dir))

    def dat2csv(self, testName, datDir, csvDir):
        self.printOut('\nProcessing Smart Terminal DAT file conversion to CSV file...')

        datFiles = [f for f in os.listdir(datDir) if f.lower().endswith('.dat')]
        # Determine the quality of DAT files process
        n_datFiles = len(datFiles)

        if n_datFiles == 0:
            self.printOut('\nThere are no DAT files detected.')
            self.printOut('Please make sure you have the copy of all the files to be processed.')
            self.printOut('Conversion aborted!')
        else:
            # Prints out the quantity of DAT files to be processed.
            self.printOut('\nNumber of DAT files to process = %d' % n_datFiles)

            if n_datFiles > 1:
                self.printOut('Too many DAT files!')
                self.printOut('Conversion aborted!')
            else:
                # Copy DAT file to CSV folder
                self.printOut('Converting DAT files...')
                self.printOut(csvDir)
                for n in range(0, n_datFiles):
                    shutil.copy((datDir + '\\' + str(datFiles[n])), csvDir)
                    # Remove whitespaces from the file names
                    # nf = csvDir + '\\' + str(datFiles[n])
                    # os.rename(nf, nf.replace(' ', '_'))

                # Renaming the copied DAT files - directly converts CSV format
                dat_csv = [f for f in os.listdir(csvDir) if f.lower().endswith('.dat')]
                for n in dat_csv:
                    src = csvDir + '\\' + n
                    # dst = csvDir + '\\' + n[:-4] + '.csv'
                    dst = csvDir + '\\' + testName + '__ST_RecordedData' + '.csv'

                    if path.exists(dst):
                        os.remove(dst)
                        self.printOut("Removed old files.")

                    # Copy the converted file to the CSV output folder
                    os.rename(src, dst)
                    self.printOut('Conversion process complete.')

                    # Scale Smart Terminal CSV file Time<ms> to Time<s>
                    self.scaleTime_csvDat(dst)

    def mat2csv(self, testName, headDir, matDir, csvDir):
        # Header Files directory
        headDir += '\\'

        # Assign header file names
        headerfile_names = ['APS2600E_header_1.csv',
                            'APS2600E_header_2.csv',
                            'APS2600E_header_3.csv',
                            'APS2600E_header_4.csv']

        # DO NOT CHANGE UNLESS NECESSARY
        # Number of samples per channel in each of the split files
        max_samples_per_channel = 10000000000

        self.printOut('\nProcessing MATLAB files conversion to CSV files...\n')

        # Check if header files exists before proceeding
        headers_exist = 1
        for h in range(0, len(headerfile_names)):
            # Get each header file paths
            headerfile_path = path.abspath(headDir + headerfile_names[h])

            if not os.path.isfile(headerfile_path):
                headers_exist = 0
                self.printOut('%s is missing!' % headerfile_names[h])

        if headers_exist:
            # Find MATLAB data folder
            n_mat_files = 0

            if not path.exists(matDir):
                self.printOut('MATLAB data folder %s is missing!' % matDir)
            else:
                # Find MATLAB files
                mat_files = [f for f in os.listdir(matDir) if f.endswith('.mat')]
                # Determine the quantity of MATLAB files to process
                n_mat_files = len(mat_files)

            if n_mat_files == 0:
                self.printOut('There are no MAT files detected.')
                self.printOut('Please make sure you have the copy of all the mat files to be processed.')
                self.printOut('Conversion aborted!')
            else:
                # Prints out the quantity of mat files to be processed.
                self.printOut('Number of MAT files to process = %d' % n_mat_files)

                # Generate MATLAB filename variable
                for mat_ix in range(0, n_mat_files):
                    filename_mat = matDir + '\\' + mat_files[mat_ix]

                    # Load file to be split
                    self.printOut('\nLoading %s' % filename_mat)
                    mat = loadmat(filename_mat)

                    # Python 3 change
                    mat_keys = list(mat.keys())
                    # Assign 'opvar' data to mat_a
                    mat_a = mat[mat_keys[0]]
                    # Transpose data
                    mat_a = np.transpose(mat_a)
                    # Obtain number of rows of data
                    n_rows = mat_a.shape[1]

                    mat_file_dummy = mat_files[mat_ix]
                    # Load headers
                    filename_number = int(mat_file_dummy[14]) - 1
                    headerfile_path = path.abspath(headDir + headerfile_names[filename_number])
                    header_names = np.loadtxt(headerfile_path, delimiter=',', dtype=str)

                    # Obtain number of rows of data
                    n_rows_header = header_names.shape[0]
                    self.printOut('Number of rows in header file = %d' % n_rows_header)
                    self.printOut('Number of rows in MAT file = %d' % n_rows)

                    # Check if the number of rows in header matches that of mat file
                    if n_rows == (n_rows_header + 1):
                        # Generate header string
                        header_string = 'Sim Time'
                        for x in range(1, n_rows):
                            signal_name = str(header_names[x - 1, 1]).strip('b\'')
                            signal_name = str(signal_name).strip('\'')
                            header_string = header_string + ',' + signal_name

                        # Acquire number of samples per channel
                        # Obtain number of rows of data
                        n_samples_per_channel = mat_a.shape[0]
                        self.printOut('Number of samples per channel = %d' % n_samples_per_channel)

                        # Check whether splitting is required
                        if n_samples_per_channel > max_samples_per_channel:
                            self.printOut(
                                'Number of samples per channel (' + str(n_samples_per_channel) + ') exceeds ' + str(
                                    max_samples_per_channel) + '.')
                            self.printOut('Splitting required.')
                            # Calculate number of files needed to be produced after splitting
                            n_files = int(n_samples_per_channel / max_samples_per_channel)
                            self.printOut(filename_mat + ' to be split into ' + str(n_files) + ' files.')

                            # Splitting Algorithm
                            for ix in range(0, n_files):
                                row_start = ix * max_samples_per_channel

                                if ix == n_files:
                                    row_end = n_samples_per_channel
                                else:
                                    row_end = (ix + 1) * max_samples_per_channel - 1

                                temp_mat = mat_a[row_start:row_end, 0:65]
                                self.printOut('Writing file ' + str(ix + 1) + ' out of ' + str(n_files) + ': ')

                                # Writing to CSV
                                # Generate CSV filename
                                filename_csv = filename_mat.split('/')[-1]
                                filename_csv = csvDir + '\\' + testName + '__' + filename_csv[:-4] + '.csv'
                                with open(filename_csv, 'wb') as f:
                                    # Write header string
                                    f.write(header_string)
                                    # Skip a line
                                    f.write('\n')
                                    # Write array data
                                    np.savetxt(f, mat_a, fmt='%.4f', delimiter=',')
                                self.printOut(filename_csv + ' has been written.')

                                temp_mat = None

                            self.printOut('Splitting and MAT to CSV conversion of ' + filename_mat + ' complete.')

                        # Splitting not required
                        else:
                            self.printOut(
                                'Number of samples per channel (' + str(n_samples_per_channel) + ') is less than ' +
                                str(max_samples_per_channel) + '. No splitting required.')
                            self.printOut('Converting ' + filename_mat)

                            # Writing to CSV
                            # Generate CSV filename
                            filename_csv = filename_mat.split('\\')[-1]
                            filename_csv = csvDir + '\\' + testName + '__' + filename_csv[:-4] + '.csv'

                            with open(filename_csv, 'wb') as f:
                                # Write header string
                                f.write(bytes(header_string, 'UTF-8'))
                                # Skip a line
                                f.write(bytes('\n', 'UTF-8'))
                                # Write array data
                                np.savetxt(f, mat_a, fmt='%.4f', delimiter=',')
                            self.printOut(filename_csv + ' has been written.')

                            # mat_a = None

                    else:
                        self.printOut('Number of rows of data does not match number of entries in ' +
                                      headerfile_names[filename_number] + '. Conversion aborted. Next file.')

                    # Emit progress bar update
                    self.progUpt(5)

                self.printOut('\nConversion process completed.')

        else:
            self.printOut('Header file(s) cannot be found. Please specify the correct path. Conversion aborted.')

    def alignData(self, csvDir):
        os.chdir(csvDir)

        self.printOut('\nAligning SMART Terminal Recorded Data...\n')
        csvList = os.listdir(csvDir)

        # Search the SCALED data file
        datScaled_f = [f for f in csvList if fm.fnmatch(f, '*_SCALED.csv')]
        # Search the CSV-converted MAT data file
        matCsv_f = [f for f in csvList if fm.fnmatch(f, '*_APS2600E_data_*_*.csv')]

        # Read the CSV-converted scaled DAT file
        with open(datScaled_f[0], 'rb') as f:
            scaledDat_df = pd.read_csv(f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)

        # Read the CSV-converted MAT files
        with open(matCsv_f[0], 'r') as f:
            matData_df = pd.read_csv(f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)

        self.printOut('STOP_CMD is at Column %d of %s.' % (matData_df.columns.get_loc('STOP_CMD'), matCsv_f[0]))
        self.printOut('Sim Time is at Column %d of %s.\n' % (matData_df.columns.get_loc('Sim Time'), matCsv_f[0]))

        # Determine the offset of 'STOP_CMD'
        matOffset = 0
        for i in range(1, matData_df.shape[0]):
            prev = matData_df['STOP_CMD'].loc[i - 1]
            curr = matData_df['STOP_CMD'].loc[i]

            if (0 == prev) & (1 == curr):
                matOffset = i
                break

        if 'a429data.stop' not in scaledDat_df.columns:
            if 'Stop' in scaledDat_df.columns:
                self.printOut('Stop variable is DETECTED instead of a429data.stop!!!')
                self.printOut('a429data.stop is at Column %d of %s.\n' % (scaledDat_df.columns.get_loc('Stop'), datScaled_f[0]))
                self.printOut('Time<sec> is at Column %d of %s.' % (scaledDat_df.columns.get_loc('Time<s>'), datScaled_f[0]))

                # Determine the offset of 'a429data.stop'
                datOffset = 0
                for i in range(1, scaledDat_df.shape[0]):
                    prev = scaledDat_df['Stop'].loc[i - 1]
                    curr = scaledDat_df['Stop'].loc[i]

                    if (0 == prev) & (1 == curr):
                        datOffset = i
                        break
            else:
                self.printOut('The SMART Terminal data variable \'a429data.stop\' was not recorded!')
            # return
        else:
            self.printOut('a429data.stop is at Column %d of %s.\n' % (scaledDat_df.columns.get_loc('a429data.stop'), datScaled_f[0]))
            self.printOut('Time<sec> is at Column %d of %s.' % (scaledDat_df.columns.get_loc('Time<s>'), datScaled_f[0]))

            # Determine the offset of 'a429data.stop'
            datOffset = 0
            for i in range(1, scaledDat_df.shape[0]):
                prev = scaledDat_df['a429data.stop'].loc[i - 1]
                curr = scaledDat_df['a429data.stop'].loc[i]

                if (0 == prev) & (1 == curr):
                    datOffset = i
                    break


        self.printOut('DAT Offset: %d' % datOffset)
        self.printOut('MAT Offset: %d' % matOffset)
        # self.printOut('Transition[Previous] %d' % scaledDat_df['a429data.stop'].loc[datOffset - 1])
        # self.printOut('Transition[Current] %d' % scaledDat_df['a429data.stop'].loc[datOffset])

        # Calculate time difference
        # Get the 'Time<s>' value at the transition point [DAT]
        xDat = float(scaledDat_df['Time<s>'].loc[datOffset])
        # Get the 'Sim Time' value at the transition point [MAT]
        xMat = float(matData_df['Sim Time'].loc[matOffset])

        timeDiff = xMat - xDat
        self.printOut('Time Difference: %f seconds' % timeDiff)

        # Alignment
        scaledDat_df['Time<s>'] += timeDiff

        # Write to a file
        af_dir = str(datScaled_f[0])[:-10] + 'ALIGNED.csv'
        scaledDat_df.to_csv(af_dir, index=False)
        self.printOut('\nFinished writing the aligned data file: %s' % af_dir)

    def mergeData(self, csvDir):
        os.chdir(csvDir)

        self.printOut('\nMerging all MATLAB data into a single file...\n')
        csvList = os.listdir(csvDir)

        # Search the CSV-converted MAT data file
        matCsv_f = [f for f in csvList if fm.fnmatch(f, '*_APS2600E_data_*_*.csv')]

        # Merge files
        result_df = pd.DataFrame(columns=['Sim Time'])
        for f in matCsv_f:
            r_df = pd.read_csv(f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)
            self.printOut('Merging %s...' % f)
            result_df = pd.merge(left=result_df, right=r_df, how='right', left_on='Sim Time', right_on='Sim Time')

            # Emit progress bar update
            self.progUpt(5)

        m_dir = (csvDir.split('\\')[-2]) + '__APS2600E_data_MERGED.csv'
        result_df.to_csv(m_dir, index=False)

        self.printOut('\nFinished merging all MATLAB data files!')
        self.printOut('%s' % m_dir)

    def plotMerge(self, csvDir):
        os.chdir(csvDir)

        testName = csvDir.split('\\')[-2]

        datCsv_f = testName + '__ST_RecordedData_ALIGNED.csv'
        matCsv_f = testName + '__APS2600E_data_MERGED.csv'

        dat_df = pd.read_csv(datCsv_f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)
        mat_df = pd.read_csv(matCsv_f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)

        dat_df = dat_df.drop('System Time', 1)

        plot_df = pd.ordered_merge(left=dat_df, right=mat_df, fill_method='ffill', left_on='Time<s>',
                                   right_on='Sim Time')

        pltCsvDir = testName + '__PLOT.csv'
        plot_df.to_csv(pltCsvDir, index=False)

        self.printOut('\nFinished writing the PLOT data in a single CSV file!')
        self.printOut('%s' % pltCsvDir)

        self.progUpt(15)

    def noMatFile(self, csvDir):
        os.chdir(csvDir)

        print('Only dat file exists!')
        # Rename _SCALED to _ALIGNED
        csvList = os.listdir(csvDir)

        # Search the SCALED data file
        datScaled_f = [f for f in csvList if fm.fnmatch(f, '*_SCALED.csv')]

        # Read the CSV-converted scaled DAT file
        with open(datScaled_f[0], 'rb') as f:
            scaledDat_df = pd.read_csv(f, index_col=False, encoding='iso-8859-1', skipinitialspace=True)

        # Write to a file
        af_dir = str(datScaled_f[0])[:-10] + 'ALIGNED.csv'
        scaledDat_df.to_csv(af_dir, index=False)

    def preProcessData(self):
        headDir = self.__headDir
        testDir = self.__testDir

        self.progUpt(0)

        # Verify the existence of Test Data Directory
        testDir = self.verifyExistDir(testDir)

        # Test name
        testName = testDir.split('\\')[-1]

        datDir = testDir + '\\' + 'dat'
        matDir = testDir + '\\' + 'mat'
        csvDir = testDir + '\\' + 'csv'

        # Make output directory if it does not exist
        if not path.exists(csvDir):
            self.printOut('Creating CSV output folder: %s' % csvDir)
            os.makedirs(csvDir)
        else:
            self.printOut('Output CSV folder: %s already exist.' % csvDir)

        # Converts the MATLAB files to CSV files
        if path.exists(matDir):
            self.mat2csv(testName, headDir, matDir, csvDir)
            self.progUpt(10)

            # Merge all MATLAB data
            self.mergeData(csvDir)
            self.progUpt(30)

            # Converts the Smart Terminal DAT file to CSV file [with MAT files]
            if path.exists(datDir):
                self.dat2csv(testName, datDir, csvDir)
                self.progUpt(10)
                # Align the data
                self.alignData(csvDir)
                self.progUpt(10)
            else:
                self.progUpt(20)
                self.printOut('No dat file to convert.')
        else:
            self.printOut('No mat file to convert.')
            self.progUpt(90)

            # Converts the Smart Terminal DAT file to CSV file [w/o MAT files]
            if path.exists(datDir):
                self.dat2csv(testName, datDir, csvDir)
                # self.noMatFile(csvDir)
                self.progUpt(10)

            else:
                self.printOut('No dat file to convert.')
                self.printOut('Are you kidding me?')
                self.progUpt(10)

        self.printOut('\nFinished processing all test data.')
        self.printOut('Proceed to analysis.')

        self.fin_out.emit()
