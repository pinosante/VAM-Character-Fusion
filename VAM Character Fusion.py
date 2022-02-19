import json
import os
import sys
import copy
import math as m
import random
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

THUMBNAIL_SIZE = 184,184
APP_WIDTH = 400
APP_HEIGHT = 628
APP_HORIZONTAL_OFFSET = 300
APP_VERTICAL_OFFSET = 300
NO_THUMBNAIL_PATH = r"no_thumbnail.jpg"

class AppWindow(tk.Frame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("VAM Character Fusion")
        self.pack(fill=tk.BOTH, expand=True)

        ###
        ### PARENT SELECTION
        ###
        self.parentselectionframe = tk.Frame(self)
        self.parentselectionframe.pack(fill=tk.X, padx=10, pady=10)

        # title
        title = {}
        for i in range(1, 3):
            title['Parent '+str(i)] = tk.Label(self.parentselectionframe, text="Parent "+str(i), font=("", 12, "bold"))
            title['Parent '+str(i)].grid(row=0, column=i-1, sticky=tk.W, pady=(0,0))

        # empty image for on the buttons
        image = Image.open(NO_THUMBNAIL_PATH)
        image = image.resize(THUMBNAIL_SIZE, Image.ANTIALIAS)
        no_thumbnail = ImageTk.PhotoImage(image)
        
        # buttons
        self.parentbutton = {}
        self.parentbutton['Parent 1'] = {}
        self.parentbutton['Parent 2'] = {}
        self.parentbutton['Parent 1']['button'] = tk.Button(self.parentselectionframe, command=lambda:self.select_file(1))
        self.parentbutton['Parent 2']['button'] = tk.Button(self.parentselectionframe, command=lambda:self.select_file(2))
        
        for i in range(1, 3):
            self.parentbutton['Parent '+str(i)]['button'].grid(row=1, column=i-1)
            self.parentbutton['Parent '+str(i)]['button'].configure(image = no_thumbnail)
            self.parentbutton['Parent '+str(i)]['button'].image = no_thumbnail
            self.parentbutton['Parent '+str(i)]['label'] = tk.Label(self.parentselectionframe, text="...")
            self.parentbutton['Parent '+str(i)]['label'].grid(row=2, column=i-1, pady=(0,0))
        
        ###
        ### CHILD SAVE FILENAME
        ###
        self.topframe = tk.Frame(self)
        self.topframe.pack(fill=tk.X, padx=10, pady=10)

        fileselection_label = tk.Label(self.topframe, text="Child", font=("", 12, "bold"))
        fileselection_label.grid(row=0, columnspan=9, sticky=tk.W, pady=(0,10))

        savefilename_label = tk.Label(self.topframe, text="Savefile Name:")
        savefilename_label.grid(row=3, column=0, sticky=tk.W)
        
        self.savefilename_entry = tk.Entry(self.topframe, width=40)
        self.savefilename_entry.grid(row=3, column=1)
        self.savefilename_entry.insert(tk.END, 'Child')

        ###
        ### OPTIONS
        ###
        self.optionsframe = tk.Frame(self)
        self.optionsframe.pack(fill=tk.X, padx=10, pady=10)
        
        options_label = tk.Label(self.optionsframe, text="Options", font=("", 12, "bold"))
        options_label.grid(columnspan=9, row=1, sticky=tk.W, pady=(0,0))

        self.parenttemplate_label = tk.Label(self.optionsframe, text="Parent Template:", anchor='w')
        self.parenttemplate_label.grid(row=2, column=0, sticky=tk.W)

        self.parenttemplate_options = ["Random Parent", "Parent 1", "Parent 2"]
        self.parenttemplate_var = tk.StringVar(self.optionsframe)
        self.parenttemplate_var.set(self.parenttemplate_options[0])
        
        self.parenttemplate_dropdown = tk.OptionMenu(self.optionsframe, self.parenttemplate_var, *self.parenttemplate_options)
        self.parenttemplate_dropdown.grid(columnspan=2, row=2, column=1, sticky=tk.W, padx=(0,0))
        self.parenttemplate_dropdown.config(width=15, anchor="w")

        self.treshold_label = tk.Label(self.optionsframe, text="Remove morphs with absolute value below:", anchor='w')
        self.treshold_label.grid(row=3, column=0, sticky=tk.W, padx=(0,0))
        
        # track if the treshold values are changed by the user and if so, update the morph info based on the setting
        self.treshold_var = tk.DoubleVar()
        self.treshold_var.trace_add("write", self.track_treshold_change)
        
        self.treshold_entry = tk.Entry(self.optionsframe, textvariable=self.treshold_var, width=7)
        self.treshold_entry.grid(row=3, column=1, sticky=tk.W)

        self.treshold_label = tk.Label(self.optionsframe, text="(0.0 = keep all)")
        self.treshold_label.grid(row=3, column=2, sticky=tk.W)        

        ###
        ### MORPH INFO
        ###
        self.morphinfoframe = tk.Frame(self)
        self.morphinfoframe.pack(fill=tk.X, padx=10, pady=0)
        
        options_label = tk.Label(self.morphinfoframe, text="Morph information", font=("", 12, "bold"))
        options_label.grid(columnspan=9, row=0, sticky=tk.W, pady=(0,0))
        
        self.totalmorphs = {}
        self.totalmorphs['Parent 1'] = {}
        self.totalmorphs['Parent 2'] = {}
        
        for i in range(1, 3):
            self.totalmorphs['Parent '+str(i)]['label'] = tk.Label(self.morphinfoframe, text="Total Morphs in Parent "+str(i)+":", anchor='w')
            self.totalmorphs['Parent '+str(i)]['label'].grid(row=2+i, column=0, sticky=tk.W)
            self.totalmorphs['Parent '+str(i)]['value'] = tk.Label(self.morphinfoframe, text="N/A", anchor='w')
            self.totalmorphs['Parent '+str(i)]['value'].grid(row=2+i, column=1, sticky=tk.W)
        
        ###
        ### GENERATE CHILD BUTTON
        ###
        self.bottomframe = tk.Frame(self)
        self.bottomframe.pack(fill=tk.X, padx=10, pady=10)

        self.generatechild = tk.Button(
            self.bottomframe, text="Generate Child", command=self.generate_child, 
            relief="flat", width=37, height=5, font=("", 12, "bold")
        )
        self.generatechild.grid(row=0, column=0, sticky=tk.W)

        self.hidegeneratechild = tk.Label(self.bottomframe, text="Generate Child", width=53, height=5)
        self.hidegeneratechild.grid(row=0, column=0)

        filler_bottom = tk.Label(self.bottomframe, text="", width=1)
        filler_bottom.grid(row=0, column=1)

        # some data variables
        self.GUIchoices = {}
        self.appearance_data = {}


    def track_treshold_change(self, var, index, mode):
        self.update_morph_info()


    def select_file(self, number):
        filetypes = (
            ('appearance files', '*.vap'),
            ('All files', '*.*'),
        )

        if 'lastpath' in self.settings:
            lastpath = self.settings['lastpath']
        else:
            lastpath = ""

        filenames = tk.filedialog.askopenfilenames(
            title = 'Open files',
            initialdir = lastpath,
            filetypes = filetypes)

        if len(filenames) == 0: # user did not select files
            self.GUIchoices['filename' + str(number)] = ""
            self.GUIchoices['filename_label' + str(number)] = ""
            self.openfile['Parent '+str(number)]['label'].configure(text = "")
            self.totalmorphs['Parent '+str(number)]['value'].configure(text = "N/A")   
            
            # if the the hidegeneratechild does not exist (allowing the user to click on the generate child button)
            # create the hidegeneratechild to make that impossible, since we were unable to load the file
            if not self.hidegeneratechild.winfo_exists():
                self.hidegeneratechild = tk.Label(self.bottomframe, text="Generate Child", width=53, height=5)
                self.hidegeneratechild.grid(row=0, column=0)
                self.generatechild.configure(relief="flat", bg="#F0F0F0")
            return 

        # user did select a file, which we are now parsing
        self.settings['lastpath'] = os.path.dirname(filenames[0])
        self.GUIchoices['filename' + str(number)] = filenames[0]
        self.GUIchoices['filename_label' + str(number)] = os.path.basename(filenames[0])[7:-4] # remove Preset_ and .vap

        self.parentbutton['Parent '+str(number)]['label'].configure(text = self.GUIchoices['filename_label' + str(number)])
        self.appearance_data['Parent '+str(number)] = load_appearance(filenames[0])
        
        # try to update the thumbnail image
        imagepath = os.path.splitext(filenames[0])[0]+'.jpg'
        self.update_thumbnail_image(number, imagepath)
        
        # stop hiding the apply changes button if both parent files are read
        if (len(self.GUIchoices.get('filename1', [])) > 0) and (len(self.GUIchoices.get('filename2', [])) > 0):
            self.hidegeneratechild.destroy()
            self.generatechild.configure(relief="raised", bg="lightgreen")
        
        self.update_morph_info()
        
        
    def update_thumbnail_image(self, number, path):
        if not os.path.exists(path):
            path = NO_THUMBNAIL_PATH
        image = Image.open(path)
        image = image.resize(THUMBNAIL_SIZE, Image.ANTIALIAS)
        thumbnail = ImageTk.PhotoImage(image)    
        self.parentbutton['Parent '+str(number)]['button'].configure(image = thumbnail)
        self.parentbutton['Parent '+str(number)]['button'].image = thumbnail

        
    def update_morph_info(self):
        treshold = self.treshold_entry.get()
        if treshold == "":
            treshold = 0
        else:
            treshold = float(treshold)
            
        for i in range(1,3):
            parentkey = "Parent "+str(i)
            if parentkey in self.appearance_data: # make sure that we already have a loaded appearance available
                if self.appearance_data[parentkey]: # make sure that the loading went ok (if not, it would be False
                    morph_tmp = copy.deepcopy(self.appearance_data[parentkey]['storables'][0]['morphs'])
                    morph_tmp = filter_morph_below_treshold(morph_tmp, treshold)
                    self.totalmorphs[parentkey]['value'].configure(text = str(len(morph_tmp)))
                else:
                    self.totalmorphs[parentkey]['value'].configure(text = "N/A")        


    def generate_child(self):
        self.get_choices_from_GUI()
        self.save_settings()
        print("Generating child")
        child = fuse_characters(self.GUIchoices['filename1'], self.GUIchoices['filename2'], self.GUIchoices)
        save_appearance(child, self.GUIchoices['Savefilename'])
        

    def get_choices_from_GUI(self):
        self.GUIchoices['Savefilename'] = os.path.join(self.settings['lastpath'], "Preset_" + self.savefilename_entry.get() + ".vap")
        self.GUIchoices['Parent Template'] = self.parenttemplate_var.get()
        if self.treshold_entry.get() == "":     
            self.GUIchoices['Treshold'] = 0
        else:
            self.GUIchoices['Treshold'] = float(self.treshold_entry.get())
        

    def save_settings(self):
        if getattr(sys, 'frozen', False):
            dir_path = os.path.dirname(sys.executable)
        elif __file__:
            dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dir_path, "settings.json")
        with open(filename, 'w') as json_file:
            print("Writing settings to:", filename)
            json.dump(self.settings, json_file, indent=3)


    def load_settings(self):
        if getattr(sys, 'frozen', False):
            dir_path = os.path.dirname(sys.executable)
        elif __file__:
            dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dir_path, "settings.json")
        if os.path.isfile(filename):
            with open(filename) as f:
                print("Reading settings from:", filename)
                self.settings = json.load(f)


def load_appearance(filename):
    if os.path.isfile(filename):
        with open(filename, encoding="utf-8") as f:
            appearance = json.load(f)
            return appearance
    return False

    
def save_appearance(appearance, filename):
    with open(filename, 'w', encoding="utf-8") as json_file:
        print("Writing appearance to:", filename)
        json.dump(appearance, json_file, indent=3)
    return True    
    

def get_mnames(morph):
    ''' returns a list with all morph names found in the list of morphs '''
    mnames = []
    for item in morph:
        mnames.append(item['name'])
    return mnames

    
def mname_in_morphs(mname, morph):
    for item in morph:
        if item['name'] == mname:
            return True
    return False


def get_uid_from_mname(mname, morphs):
    ''' look through list of morphs for mname and returns the first found corresponding uid '''
    for morph in morphs:
        for item in morph:
            if item['name'] == mname:
                return item['uid']
    return False
    

def add_mnames_to_morphs(morphs, merged_mnames):
    ''' adds uid keys to each morph in morphs and sets the values to 0 if uid key doesn't exist '''
    mnames = []
    morphs = copy.deepcopy(morphs)
    
    for morph in morphs:
        to_add = []
        for mname in merged_mnames:
            if mname_in_morphs(mname, morph):
                #print("{} in morph, {}".format(mname, get_uid_from_mname(mname, morphs)))
                continue
            else:
                new_item = {
                    'uid': get_uid_from_mname(mname, morphs),
                    'name': mname,
                    'value': '0.0'
                }
                to_add.append(new_item)
        morph.extend(to_add)
    return morphs
          
def intuitive_crossover(morph1, morph2):
    ''' returns a new morph which is the combined morph of morph1 and morph2 where each gene has 0.5 chance to be selected '''
    new_morph = []
    for i in range(len(morph1)):
        if random.randint(0, 1):
            new_morph.append(morph1[i])
        else:
            new_morph.append(morph2[i])
    return new_morph
    
def non_uniform_mutation(morph):
    ''' select a random gene, and apply non_uniform mutation to it '''
    morph = copy.deepcopy(morph)
    
    index = random.choice(range(len(morph)))
    value = morph[index]['value']
    
    b = 0.5
    r1 = random.random()
    r2 = random.random()
    
    if (r1 >= 0.5):
        value = (1.0 - float(value)) * r2 * b
    else:
        value = (0.0 + float(value)) * r2 * b
    value = str(value)
    morph[index]['value'] = value
    return morph

    
def save_morph_to_appearance(morph, appearance):
    appearance = copy.deepcopy(appearance)
    appearance['storables'][0]['morphs'] = morph
    return appearance
    
def dedupe_morphs(morphs):
    morphs = copy.deepcopy(morphs)
    new_morphs = []
    for morph in morphs:
        new_morph = []
        found = []
        found_items = {}
        for item in morph:
            if item['name'] in found:
                continue
            else:
                found.append(item['name'])
                found_items[item['name']] = item
                new_morph.append(item)
        new_morphs.append(new_morph)
    return new_morphs

    
def count_morphvalues_below_treshold(morph, treshold):
    ''' checks for each item in morph if the absolut value is below the treshold  and returns a count and percentage '''
    count = 0
    percentage = 0
    
    for item in morph:
        if abs(float(item['value'])) < treshold:
            count += 1
    percentage = count / len(morph)
    return count, percentage

    
def filter_morph_below_treshold(morph, treshold):
    ''' goes through each item in each morph in the list of morphs and only keeps items with values above treshold '''
    morph = copy.deepcopy(morph)
    new_morph = []
    for item in morph:
        if abs(float(item['value'])) < treshold:
            continue
        else:
            new_morph.append(item)
    return new_morph


def fuse_characters(parent1, parent2, options):
    treshold = options['Treshold']
    files = []
    files.append(parent1)
    files.append(parent2)
    
    morphs = []
    for i, f in enumerate(files):
        print("Reading appearance:", f)
        appearance = load_appearance(f)
        morph = appearance['storables'][0]['morphs']
        morph = filter_morph_below_treshold(morph, treshold)    
        morphs.append(morph)
    
    mnames = []
    for morph in morphs:
        mnames.extend(get_mnames(morph))
        count, percentage = count_morphvalues_below_treshold(morph, treshold)
        
    mnames = list(dict.fromkeys(mnames)) # remove duplicates but keep the same order
    
    morphs = dedupe_morphs(morphs)
    
    morphs = add_mnames_to_morphs(morphs, mnames)
    sortedmorphs = []
    for morph in morphs:
        sortedmorphs.append(sorted(morph, key=lambda d: d['name']))
        
    childmorphs = intuitive_crossover(sortedmorphs[0], sortedmorphs[1])
    childmorphs = non_uniform_mutation(childmorphs)
    
    # select parent template
    if options["Parent Template"] == "Random Parent":
        index = random.choice(range(len(files)))
    elif options["Parent Template"] == "Parent 1":
        index = 0
    elif options["Parent Template"] == "Parent 2":
        index = 1
    else:
        print("Something unexpected happened.")
    
    child = load_appearance(files[index])
    print("Using as appearance template:", files[index])
    child = save_morph_to_appearance(childmorphs, child)
    return child


def main():
    root = tk.Tk()
    app_dimensions = str(APP_WIDTH)+"x"+str(APP_HEIGHT)+"+"+str(APP_HORIZONTAL_OFFSET)+"+"+str(APP_VERTICAL_OFFSET)
    
    root.geometry(app_dimensions)
    root.iconbitmap("VAM Character Fusion.ico")    
    app = AppWindow()

    app.settings = {}
    app.load_settings()
    root.mainloop()
    app.save_settings()

if __name__ == '__main__':
    main()