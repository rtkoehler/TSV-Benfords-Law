#!/usr/bin/python3.9

import os
import re
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from scipy.stats import chi2_contingency


class BenfordsLaw:
    """
    This is a class that handles the mathematics behind testing if a submitted dataset follows Benford's Law.

    Attributes:
        file_path (string): the string representation of where the file being tested is stored.
        first_number_list (list[int]): the collection of leading numbers in the dataset.
        observed_ratios (list[int]): the collection of ratios of the numbers in first_number_list.
        EXPECTED_RATIO (int): the constant, expected ratio of numbers, being 1/9.
        BENFORDIAN_RATIOS (list[double]): the constant list of doubles reported in Benford's paper.
    """

    def __init__(self, file_path):
        """
        The constructor for the BenfordsLaw class.

        Parameters:
            file_path (string): the string representation of where the file being tested is stored.
        """
        self.file_path = file_path
        self.first_number_list = []
        self.observed_ratios = []
        self.EXPECTED_RATIO = 1 / 9
        self.BENFORDIAN_RATIOS = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

    def get_numbers_from_data_regex(self, ignore_first_line):
        """
        The function that executes the "safe" regex search.
        
        Parameters:
            ignore_first_line(bool): a boolean deciding whether to keep or ignore the top row of the dataset.
        Returns:
            True upon completion.
        """
        all_numbers_list = []
        with open(self.file_path, 'r') as f:
            if ignore_first_line:
                next(f)
            for line in f:
                # Blindly grab every number from file
                number_in_line = re.search("[\d]+", line)
                all_numbers_list.append(number_in_line.group())
        for data in all_numbers_list:
            first_number = int(data[0])
            self.first_number_list.append(first_number)
        return True

    def get_numbers_from_data_tsv(self, column_to_collect, ignore_first_line):
        """
        The function that executes the "unsafe" search and uses more logic than the regex search.
        
        Parameters:
            column_to_collect(int): a zero-indexed integer that the user
            wants to use for the dataset.
            ignore_first_line(bool): a boolean deciding to keep or ignore the top row of
            the dataset.

        Returns: True upon completion.
        """

        data_list = []
        i = 0
        try:
            with open(self.file_path, 'r') as f:
                if ignore_first_line:
                    next(f)
                    i += 1
                for line in f:
                    i += 1
                    # Removes tabs, double or more spaces, and single spaces before an integer.
                    # Aims to cover mistakes made in making the tab separated file.
                    separate_non_single_space_whitespace = re.sub("\t+|\s{2,}|\s(?=\d)", "~~~", line)
                    data_list.append(re.split("~~~", separate_non_single_space_whitespace))
        except InvalidLine:
            print("Line " + str(i) + " has a formatting issue. Please make sure each column is TAB separated.")
            for column in data_list:
                first_number = int(column[column_to_collect][0])
                self.first_number_list.append(first_number)
            return True

    def get_ratios(self):
        """
        The function that gets the observed ratios from the dataset.

        Returns:
            True upon completion.
        """
        observed_counts = Counter(self.first_number_list)
        data_length = len(self.first_number_list)
        for i in range(1, 10):
            ratio = observed_counts[i] / data_length
            self.observed_ratios.append(ratio)
        return True

    def plot_data(self):
        """
        The function that plots the expected ratios and the observed ratios.

        Returns:
            True upon completion.
        """
        labels = (i for i in range(1, 10))
        observed_sizes = self.observed_ratios
        expected_sizes = [self.EXPECTED_RATIO] * 9
        print(observed_sizes, expected_sizes)
        index = np.arange(9)
        bar_width = 0.4
        observed_bars = plt.bar(index, observed_sizes, bar_width, color='r')
        expected_bars = plt.bar(index + bar_width, expected_sizes, bar_width, color='g')
        plt.xlabel('Leading Digit in Dataset')
        plt.ylabel('Ratio')
        plt.title('Expected Versus Observed Leading Number in Dataset')
        plt.xticks(index + bar_width, labels)
        plt.legend((observed_bars[0], expected_bars[0]), ("Observed Ratio", "Expected Ratio"))
        plt.tight_layout()
        plt.show()
        return True

    def is_dataset_benfordian_chi_squared_accept_null(self):
        """
        The function that runs a chi-square test for mathematical evidence for dataset being Benfordian or not.

        Returns:
            True or False based on if the null hypothesis should be rejected or not.
        """
        data = [self.observed_ratios, [self.EXPECTED_RATIO] * 9]
        stat, p, dof, array = chi2_contingency(data)
        alpha = 0.05
        if alpha >= p:
            return False
        else:
            return True


class InvalidChoice(Exception):
    """This class serves to be an exception when a user inputs a wrong choice."""
    pass


class NotAFilePath(Exception):
    """This class serves to be an exception when a user inputs a file path that can't be a file"""
    pass


class InvalidLine(Exception):
    """This class serves to be an exception when a user inputs a file that is not formatted correctly"""
    pass


def introduction():
    """ 
    This function serves to run the greeting logic for the main() function. 
    
    Returns:
        user_choice: a string literal of the selection the user wants to execute.
    """
    print("Hello user! Welcome to the Benford's Law tester!")
    print("Please let me know if you wish to use the default file provided or if you wish to provide a tab separated "
          "file.")
    valid_choice = False
    user_choice = ''
    while not valid_choice:
        try:
            valid_choices = ['1', '2', '3', '4']
            user_choice = input("Please enter \n" +
                                "1 for the pre-formatted file:\n" +
                                "2 to enter the path to your tab separated file:\n" +
                                "3 to learn more about the requirements to use your tab separated file:\n" +
                                "4 to enter your own file in order to use a riskier algorithm.\n")
            if user_choice not in valid_choices:
                raise InvalidChoice
            else:
                valid_choice = True
        except InvalidChoice:
            print("Please enter a valid choice...\n")
    return user_choice


def act_on_selection(users_choice):
    """
    This function handles the execution of the choice the user makes in introduction().

    Parameter:
            users_choice(str): a string literal containing the option the user wants.
    Returns:
        True upon completion.
    """
    if users_choice == '1':
        run_safe_algorithm('/home/ryan/Documents/L7/census_2009.txt', True)
    elif users_choice == '2':
        users_file_path = check_file_path()
        run_safe_algorithm(users_file_path, False)
    elif users_choice == '3':
        explain_formatting()
    elif users_choice == '4':
        users_file_path = check_file_path()
        column_to_collect = int(input("Please enter the (zero-indexed) column you wish to use:\n"))
        run_risky_algorithm(users_file_path, column_to_collect)
    return True


def run_risky_algorithm(file_path, column_to_collect):
    """
    This function handles the logical flow and execution of the riskier algorithm.

    Parameters:
        file_path(str): a string with the path to the data file.
        column_to_collect(int): a string representation of a zero-indexed number of the column the user wants to use.

    Returns:
        True upon completion.
    """
    user = BenfordsLaw(file_path)
    ignore_top_line = ask_about_top_line()
    user.get_numbers_from_data_tsv(column_to_collect, ignore_top_line)
    user.get_ratios()
    user.plot_data()
    accept_null = user.is_dataset_benfordian_chi_squared_accept_null()
    do_chi_squared_announcement(accept_null)
    return True


def run_safe_algorithm(file_path, default_file):
    """
   This function handles the logical flow and execution of the safer algorithm.

   Parameters:
       file_path(str): a string with the path to the data file.
       default_file(bool): a boolean that represents if the default file is being ran.

   Returns:
       True upon completion.
   """

    plotter = BenfordsLaw(file_path)
    if default_file:
        top_line_is_headers = True
    else:
        top_line_is_headers = ask_about_top_line()
    plotter.get_numbers_from_data_regex(top_line_is_headers)
    plotter.get_ratios()
    plotter.plot_data()
    null_acceptance = plotter.is_dataset_benfordian_chi_squared_accept_null()
    do_chi_squared_announcement(null_acceptance)
    return True


def explain_formatting():
    """ 
    This function simply outputs the expected file to be used in this program. 
    
    Returns:
        True upon completion.
    """
    print("\nThese are the requirements that your TAB separated file must contain for this program to function:\n" +
          "\t1.) Each column must be separated by tabs.\n" +
          "\t2.) Each column must contain only numeric or only alphabetical data.\n" +
          "\t3.) The top row's column can either contain or omit descriptors.")
    print("If these requirements are not met, there is no guarantee that this program will behave as expected.\n")
    print("However, there is an option to try an alpha-level algorithm that may or may not work with your improperly "
          "formatted file.")
    print("This alpha-level algorithm has the advantage of having more control over which column is used, "
          "but is still not recommended")
    return True


def do_chi_squared_announcement(null_acceptance):
    """
    This function simply lets the user know if the data set is likely to be Benfordian.

    Parameter:
        null_acceptance(bool): a boolean determining if the null hypothesis should be accepted or not
    
    Returns:
        True upon completion.
    """
    print("Using a chi squared test and the null hypothesis that this dataset provides non-Benfordian leading "
          "numbers...")
    if null_acceptance:
        print("There is evidence that this dataset follows Benford's Law")
    else:
        print("There is not evidence that this dataset follows Benford's Law")
    return True


def check_file_path():
    """
    This function acts as a simple check to see if they user is pointing the program to a file.
    It also servers as a subtle reminder that a TAB separated file is needed.

    Returns:
        True upon completion.
    """
    users_file_path = ""
    valid_file_path = False
    while not valid_file_path:
        try:
            users_file_path = input("Please enter the path of your tab separated and correctly formatted file:\n")
            if not os.path.isfile(users_file_path):
                raise NotAFilePath
            valid_file_path = True
        except NotAFilePath:
            print("Please enter a valid file path.\n")
    return users_file_path


def ask_about_top_line():
    """
    This function asks the user to specify if the top row in the file is data or not.

    Returns:
        is_top_row_column_titles(bool): a boolean that determines if the top line of a file is ignored.
    """
    is_top_row_column_titles = False
    valid_choice = False
    valid_choices = ['1', '2']
    while not valid_choice:
        try:
            user_input = input("Please enter: \n" +
                               "1 if your file's top row is column titles\n" +
                               "2 if your file's top row is filled with data: \n")
            if user_input not in valid_choices:
                raise InvalidChoice
            else:
                valid_choice = True
            if user_input == '1':
                is_top_row_column_titles = True
        except InvalidChoice:
            print("please enter a valid choice")
    return is_top_row_column_titles


def main():
    """The main function."""
    user_choice = introduction()
    act_on_selection(user_choice)


main()
