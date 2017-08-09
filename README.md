## QuickManga  
It's a simple program which lets you read your favorite manga from [MangaPanga][Manga Panda].  

### Features  
* Test the latest release of manga with one line command
* Read Latest release of a manga with only one command
* Download specific episodes of a manga


### Dependencies  
All dependencies are in requirements.txt, Install It with:  
>pip install -r requirements.txt  

>* _feh_
>>sudo apt-get install feh  
>>sudo pacman -S feh  

### Usages:  
Search Manga By Name  
>./quickmanga.py -S "One Piece"  
>./quickmanga.py -S Naruto  

List Episodes  
>./quickmanga.py -L /one-piece  
>./quickmanga.py -L /hunter-x-hunter  

Download Episodes  
>./quickmanga.py -D /one-piece -E 1,10,100,500  
>./quickmanga.py -D /naruto -E *  
*'\*' downloads all episodes  

Read Episodes  
>./quickmanga.py -R /one-piece -E 750  
>./quickmanga.py -R /hunter-x-hunter -E 100  
*Downloads and opens episodes in _feh_


[Manga Panda]:www.mangapanda.com
