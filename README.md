# VAM-Character-Fusion <img align="right" width="400" height="658" src="https://i.imgur.com/alovBTG.png">
Take two Virtuamate characters and fuse them together to create a child character with properties (morphs) of both parents. 

# How do I use this?
1. When you start the app, click on the left silhouette, and go to your Virtuamate Appearance directory (e.g.: `C:\VaM\Custom\Atom\Person\Appearance` or something).
2. Click on the appearance you want to load.
3. Do the same for the right silhouette.
4. Now the "Generate Child" button will become green, click on it.
5. Congratulations! You now have a beautiful "Child" of both parent appearances (left and right). 

You can find the Child appearance card in the last folder you used when loading an appearance. It is named `Preset_Child.vap` and it has a fancy generic "VAM Character Fusion Child" thumbnail.

# What do the options do?
**Save filename**

By default each child is named Child (`Preset_Child.vap` to be precise). But you can use your own custom name if you want.

**Parent Template**

This lets you choose which appearance file you want to use as the base appearance for your child. The child will inherit from the chosen parent appearance file: the  clothing, hair, eyes, makeup, skin, height, etc. Basically everything which is *not* a morph. The only changed values for the child, will be the new morphs chosen from both parents.
Available choices are: Parent 1 (child's will only use this as a template), Parent 2 (child's will only use this as a template), or Random Parent (each child will randomly use the appearance of Parent 1 or Parent 2 as a template).

**Remove morphs with absolute value below**

Some appearances have a lot of morphs which are really close to zero. If you would keep those, there is a lot of morphs which would not do anything for the child when chosen or mutated. For this reason I'd advice to keep this value at the default of 0.01 to make sure to delete the most insignificant morphs from the appearance, resulting in more variation in the childs you create. If you want to keep all the morphs anyway, just enter 0 in this box or keep it empty.

# What do I do with the Morph information?
Here the total amount of morphs found in each parent is shown (after removing all morphs with an absolute value below the set treshold). This is a good indicator of the amount of custom morphs the parent has. If a parent has a small amount of morphs (say, smaller than 50), there is a big chance that the "look" has been saved into a few custom morphs especially for this character. Parents with such specific custom morphs are not really suited for child generation since there is only 1 or 2 "genes" which decide the look, namely the custom morph. If you generate a child from such a parent, you either copy the whole look (if the morph was randomly chosen for your child), or lose the whole look (if the morph was *not* randomly chosen for your child). Long story short: try to use parents with a total amount of morphs, larger than, say 100. You can do that by looking at the Morph information when you load your parents.

# How does your program work?
Thanks for asking! In a nutshell it works like this.
1. Load two appearances.
2. Extract all morphs from each appearance.
3. Depending on if you use a treshold, keep all these morphs, or remove those morphs which have an absolute value below the set treshold.
4. Combine all remaining morphs of both appearances into a single list.
5. Remove all duplicate morphs from this list.
6. Keep adding morphs from this list to both appearances, until both appearances contain all the morphs in the list from the above step.
7. If a morph is new for an appearance (because it originally came from the other appearance), set it 0.
8. Now we do crossover: create the morphs for the child, by looping through all the available morphs in the list from (5) and randomly copying the values from this morph from either parent 1 or parent 2.
9. After that, apply mutation: this is a non uniform mutation. This link explains how it works https://www.geeksforgeeks.org/mutation-algorithms-for-real-valued-parameters-ga/. Very simply put you choose one morph at random, and changes it number while making sure the random chosen number stays between 0.0 and 1.0. I use `b = 0.5` as a parameter btw.
10. Choose the appearance either from parent 1 or parent 2 (depending on the choice for "parent template" by the user.
11. Overwrite the morphs from that appearance by the generated morphs for the child.
12. Save the new child appearance.

# Are you a professional coder?
Hah! If you would look at the code, you would know the answer. Which is: no.

# Can I help you, or give feedback on your code?
Yes, please. I'd love to improve my coding skills.
