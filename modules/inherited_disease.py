#!/usr/bin/env python3

import argparse
from gettext import find
from subprocess import list2cmdline
import pandas as pd
from version import __version__
import panels.sheep_panel as sheep
import panels.cow_panel as cow
import panels.goat_panel as goat
# import time



def species_df(data,species):
    sp_df=data[data['Sample Name'].str.contains(species)]
    return(sp_df)

def filter_for_ID(host,df):
    host_df=df[["Sample Name","Allele Name","Allele Call"]]
    wide_host=host_df.pivot(index='Sample Name',columns='Allele Name',values='Allele Call')
    if host == "Cow":
        wide_host=wide_host[wide_host.columns.intersection(cow.cow_panel)]
    elif host == "Goat":
        wide_host=wide_host[wide_host.columns.intersection(goat.goat_panel)]
    elif host == "Sheep":
        wide_host=wide_host[wide_host.columns.intersection(sheep.sheep_panel)]
    return(wide_host)

def find_loc(df):
    list_of_locs=[]
    for index, row in df.iterrows():
        if row['Allele Call'] == 'Heterozygous' and row.Frequency > 0 and row.Frequency < 40 or row['Allele Call'] == 'Heterozygous' and row.Frequency > 60 and row.Frequency < 100:
            list_of_locs.append([row['Sample Name'],row['Allele Name'],row.Frequency,row.Quality])
        elif row.Quality < 80:
            list_of_locs.append([row['Sample Name'],row['Allele Name'],row.Frequency,row.Quality])
    return(list_of_locs)

def reformat_df(df):
    df=df.replace("Heterozygous","Carrier")
    df=df.replace("Homozygous","Affected")
    df=df.replace("Absent","Normal")
    return(df)
    # return(highlight_no_call(df))

### Formatting styles
# def highlight_no_call(df):
#     df=df.style.applymap(lambda x: 'background-color : yellow' if x == "No Call" else '')
#     return(df)
#     # return(lambda x: 'background-color : yellow' if x == "No Call" else '')

def highlight_loc(list_of_locs,df):
    color = 'background-color: orange'
    for pair in list_of_locs:
        try:
            df.loc[pair[0], pair[1]] = color
        except:
            continue
    # return(df)

def test_highlight(val):
    if val == "No Call":
        colour = 'yellow'
    # elif val == "Affected":
    #     colour = 'green'
    # elif val == "Carrier":
    #     colour = 'orange'
    else:
        return
    return(f'background-color: {colour}')

def create_log(locs,animal,df):
    """
    Temporary function to create a log of markers that don't meet criteria until colour formatting is added
    """
    print(f"Writing log for markers that require checking to log_{animal}.txt")
    with open(f"log_{animal}.txt",'w') as fh:
        for pair in locs:
            if pair[3] < 80:
                try:
                    call=df.loc[pair[0], pair[1]]
                    fh.write(f'QUALITY: Sample {pair[0]} for {call} marker {pair[1]} is below Quality of 80')
                    fh.write('\n')
                except:
                    continue
            else:
                try:
                    call=df.loc[pair[0], pair[1]]
                    fh.write(f'FREQUENCY: Sample {pair[0]} for {call} marker {pair[1]} is outside of frequency 40-60%')
                    fh.write('\n')
                except:
                    continue


def run(input):
    print('Reading in Data')
    data=pd.read_excel(input,header=0)
    find_loc(data)
    for animal in ['Cow','Goat','Sheep']:
        print(f"Filtering data for {animal} samples")
        df=species_df(data,animal)
        filt_df=filter_for_ID(animal,df)
        if not len(filt_df.columns) == 0:
            # print(len(filt_df.columns))
            locs=find_loc(df)
            format_df=reformat_df(filt_df)
            format_df=format_df.style.applymap(test_highlight)
            create_log(locs,animal,filt_df)
        # format_df=reformat_df(filt_df)
        # format_df.style.apply(highlight_loc, axis=None)
            format_df.to_excel(f'{animal}_output.xlsx')
        else:
            print(f'No samples for found for host: {animal}')


def main():
    description=f"""
    Pipeline for analysis of inherited disease panels \n
    Version: {__version__}"""
    parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter, add_help=False)

    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-i", "--input", help="input")

    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")

    args=parser.parse_args()
    input=args.input

    run(input)



if __name__ == '__main__':
    main()