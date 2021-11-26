import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import os
import seaborn as sns
import numpy as np
import configparser
import time
import sys

class WoodDensity():

    
          

    def __init__(self):
        self._parse_conf()
        self.path = self.parser.get("config", "path")
        self.outputpath = self.parser.get("config", "output_path")
        self.labeldf = self.parser.get("config", "label_path")
        self.fig_folder = self.parser.get("config", "fig_folder")

        self.listoffiles =self._listdir_fullpath() 

    def _parse_conf(self):
        '''
        parse the conf file
        '''
        
        self.parser = configparser.ConfigParser()
        self.parser.read("conf") 

    def _listdir_fullpath(self):
        '''
        method for creating a list of pxb file
        '''
        import os
        return [f for f in os.listdir(self.path) if f.endswith('.pxb')]

    def __str__(self): # print info
        return "\nSpecified path is : {}, number of pxb files detected: {}\noutput path is: {}\n".format(self.path, len(self.listoffiles),  self.outputpath)

    def _plot_file(self, y):
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15,15)) 
        except:
            fig, (ax1, ax2) = plt.subplots(1, 2)

        ax1.plot(y)
        sns.kdeplot(axes = ax2, data = y, fill=True, common_norm=False, alpha=.5)

        plt.show(block=False)
        selected_points = fig.ginput(2)                  
        #plt.waitforbuttonpress(0)
        plt.close('all')

        maxpts = int(np.maximum(selected_points[0][0], selected_points[1][0]))
        minpts = int(np.minimum(selected_points[0][0], selected_points[1][0]))
        print('2 points were selected, min: {}, max: {}\n'.format(minpts,maxpts))        

        return maxpts, minpts

    def _save_file(self, y, sample, maxpts, minpts):

        
        figb, (ax1b, ax2b, ax3b) = plt.subplots(1, 3)       
        
        ax1b.plot(y)
        sns.kdeplot(ax = ax2b, data = y, fill=True, common_norm=False, alpha=.5)
        sns.kdeplot(ax = ax3b, data = y[minpts+1:maxpts], fill=True, common_norm=False, alpha=.5)
        ax1b.set_title('wood $d$ \nprofile')
        ax2b.set_title('raw wood $d$\ndistribution')
        ax3b.set_title('filtered wood \n$d$ distribution')


        verts = [[0, min(y)],[minpts, min(y)], [minpts, max(y)], [0, max(y)]]
        poly = Polygon(verts, facecolor='grey', alpha = 0.5)
        ax1b.add_patch(poly)  

        verts = [[maxpts,  min(y)],[len(y),  min(y)], [ len(y), max(y)], [maxpts, max(y)] ]
        poly = Polygon(verts, facecolor='grey', alpha = 0.5)
        ax1b.add_patch(poly)
        
        #print('2 points were selected, min: {}, max: {}\n'.format(minpts,maxpts))
        #print(len(y))
        #print(len( y[minpts:maxpts]))

        plt.tight_layout()

        plt.savefig(os.path.join(self.outputpath, self.fig_folder, str(sample)+'.png'), dpi = 420, bbox_inches = 'tight')
        
        plt.close('all')

    
    def _plot_save_file(self, y, sample):

        try:
            sample = int(sample)
        except:
            pass

        maxpts, minpts = self._plot_file(y)

        self._save_file(y, sample, maxpts, minpts)
        
        
        #ax1.vlines(minpts, min(y), max(y), lw=3)
        #ax1.vlines(maxpts, min(y), max(y), lw = 3)  fig, (ax1, ax2) = plt.subplots(1, 2)  
        
        return maxpts, minpts
    

    def _create_dir(self):
        import os
        if not os.path.exists(os.path.join(self.outputpath, self.fig_folder)):
                os.makedirs(os.path.join(self.outputpath, self.fig_folder))
                

    def _check_files(self):
        failed = []
        for f in self.listoffiles:
                df = pd.read_csv(os.path.join(self.path,f), sep = '\t', header = 0, names = ['density', 'wood'], skiprows = 8, usecols=[0, 1])

                try:
                    pd.to_numeric(df.density)
                except:
                    #print('error, check the file: {}'.format(f))
                    failed.append(f)
        if len(failed)>0:
            print('------------------------------------\nError, some files need to be checked\n------------------------------------\n')
            [print(fi) for fi in failed]
            print('\n')
            raise Exception('Some files need to be checked')
        else:
            print('------------------------------------\nFiles checked, seems OK!\n------------------------------------\n')

    def _update_progress(self, progress):
        barLength = 20 # Modify this to change the length of the progress bar
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float"
        if progress < 0:
            progress = 0
            status = "Halt..."
        if progress >= 1:
            progress = 1
            status = "Done..."
        block = int(round(barLength*progress))
        text = "\rPercent: [{0}] {1:.2f}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()


    def read_file_write_bound(self):
        import pandas as pd
        import numpy as np
        
        self._check_files()

        self._create_dir()
        #CREATE AN EMPTY DF empty_df = 

        _col_header =  np.array(['SAMPLE', 'THICKNESS mm', 'SLITLENGTH mm', 'SLITWIDTH mm', 'HPIXELSIZE mm', 'VPIXELSIZE mm', 'MIN', 'MAX'])

        df_header = pd.DataFrame(columns = _col_header)
        df_data = pd.DataFrame(columns = ['sample', 'density', 'wood', 'keepit', 'year'])
        prog = 0
        total_file = len(self.listoffiles)

        for f in self.listoffiles:

            print('n')

            prog += 1
            time.sleep(0.01)
            self._update_progress(prog/total_file)


            print(f)

            df = pd.read_csv(os.path.join(self.path,f), header = 0, names = ['var','value'], sep = '\t', nrows = 6, usecols=[0, 1])

            for i in _col_header:
                try:
                    i in df['var'].values
                except:
                    print('{} not in variables'.format(i))
            
            _sample = df.loc[df['var'] == 'SAMPLE', 'value'].values[0]
            _thickness = df.loc[df['var'] == 'THICKNESS mm', 'value'].values[0]
            _slitlength = df.loc[df['var'] == 'SLITLENGTH mm', 'value'].values[0]
            _slidwidth = df.loc[df['var'] == 'SLITWIDTH mm', 'value'].values[0]
            _hpixelsize = df.loc[df['var'] == 'HPIXELSIZE mm', 'value'].values[0]
            _vpixelsize = df.loc[df['var'] == 'VPIXELSIZE mm', 'value'].values[0]

            #print([_sample, _thickness, _slitlength])


            df = pd.read_csv(os.path.join(self.path,f), sep = '\t', header = 0, names = ['density', 'wood'], skiprows = 8, usecols=[0, 1])

            # plot and save
            maxpts, minpts = self._plot_save_file(df.density, sample = _sample)

            parametersVal = [_sample, _thickness, _slitlength, _slidwidth, _hpixelsize, _vpixelsize, minpts, maxpts]

            df_header = df_header.append({k:v for k,v in zip(_col_header, parametersVal)}, ignore_index = True)

            df['sample'] = _sample

            # filter the df based on selected points
            df['keepit'] = [1 if (i>minpts) & (i < maxpts) else 0 for i in df.index]

            # create a new column with year value
            maskyear = [year if year != 0 and year != 1 else None for year in df.wood]
            df['year']= maskyear
            df['year']= df['year'].ffill()
            df.loc[df['year'].isna(), 'year']= df['year'].min() -1
            
            # replace year values in wood columns with 0
            df['wood'] = [0 if year != 0 and year != 1 else year for year in df.wood]

            df_data = pd.concat([df_data, df])

            print(df_header)
            print(df_data)
        
            df_header.to_csv(os.path.join(self.outputpath,'dfheader.csv'))
            df_data.to_csv(os.path.join(self.outputpath,'dfdata.csv'))


        self.df_header = df_header 
        self.df_data =   df_data

        # SAVE DF 

    def label_df(self):
        import matplotlib.pyplot as plt
        import seaborn as sns
        #print(self.labeldf) 
        if self.labeldf == 'NULL':
            print('no label provided, skip this step')
        else:
            dfwithlabel = pd.read_csv(self.labeldf, sep = ",")
            dfwithlabel = dfwithlabel[['label','sample']]

            result = pd.merge(self.df_data, dfwithlabel, on="sample")
            print(result.loc[result['keepit']==1,['density', 'label','year', 'wood']].groupby(['label','year', 'wood' ]).mean())
            result.loc[result['keepit']==1,['density', 'label','year', 'wood']].groupby(['label','year', 'wood' ]).mean().plot(kind = 'bar' )
            plt.show(block = False)
            plt.waitforbuttonpress(0)
            plt.close('all')
            result.to_csv(os.path.join(self.outputpath,'density.csv'))
        
            
