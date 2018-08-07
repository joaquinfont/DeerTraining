f r o m   n u m p y   i m p o r t   * 
 f r o m   m a t p l o t l i b . p y p l o t   i m p o r t   * 
 f r o m   B i c y c l e M o d e l   i m p o r t   * 
 f r o m   s c i p y . o p t i m i z e   i m p o r t   m i n i m i z e 
 f r o m   B i n a r y C o n v e r s i o n   i m p o r t   * 
 i m p o r t   c o p y 
 
 c l a s s   M P C _ G : 
         d e f   _ _ i n i t _ _ ( s e l f ,   N p = 5 ,   d t p = . 5 ,   q _ o b s t a c l e _ e r r o r   =   1 . 0 ,   q _ c r u i s e _ s p e e d   =   1 . 0 ,   q _ x _ a c c e l = 1 . 0 ,   g a s _ m a x = 1 . 0 ,   b r a k e _ m a x   =   . 5 ,   e p s i l o n   =   0 . 0 0 0 1 ) : 
                 s e l f . N p   =   N p 
                 s e l f . d t p   =   d t p 
                 s e l f . q _ o b s t a c l e _ e r r o r   =   q _ o b s t a c l e _ e r r o r 
                 s e l f . q _ c r u i s e _ s p e e d   =   q _ c r u i s e _ s p e e d 
                 s e l f . q _ x _ a c c e l   =   q _ x _ a c c e l 
                 s e l f . g a s _ m a x   =   g a s _ m a x 
                 s e l f . b r a k e _ m a x   =   b r a k e _ m a x 
                 s e l f . e p s i l o n   =   e p s i l o n 
                 s e l f . p r e d i c t i o n _ t i m e   =   s e l f . d t p * s e l f . N p 
                 s e l f . t _ h o r i z o n   =   a r a n g e ( 0 , s e l f . p r e d i c t i o n _ t i m e , s e l f . d t p ) # g o   t o   o n e   e x t r a   s o   t h e   h o r i z o n   m a t c h e s 
 
         d e f   p r e d i c t D e e r _ s t a t i c ( s e l f , d e e r n o w , c a r n o w ) : 
                 p r e d i c t D e e r   =   c o p y . d e e p c o p y ( d e e r n o w ) 
                 # m a k e   a   t i m e   v e c t o r   f o r   p r e d i c t i o n   u s i n g   ' f i n e '   t i m e s t e p   o f   d e e r 
                 t v e c   =   a r a n g e ( 0 , s e l f . p r e d i c t i o n _ t i m e + p r e d i c t D e e r . d T , p r e d i c t D e e r . d T ) 
                 # i n i t i a l i z e   t h e   ' f i n e '   p r e d i c t e d   s t a t e   v e c t o r 
                 x d e e r _ p r e d   =   z e r o s ( ( l e n ( t v e c ) , 4 ) ) 
                 f o r   k   i n   r a n g e ( 0 , l e n ( t v e c ) ) : 
                         # e v e n t u a l l y ,   t h e   d e e r   w i l l   n e e d   t o   a l s o   h a v e   a   m o d e l   o f   h o w   t h e   C A R   m o v e s . . . 
                         x d e e r _ p r e d [ k , : ]   =   p r e d i c t D e e r . x d e e r 
                 # n o w   d o w n s a m p l e   t h e   p r e d i c t i o n   s o   t h a t   t h e   h o r i z o n   m a t c h e s   M P C   r a t h e r   t h a n   t h e   d e e r 
                 # t h i s   w a y ,   t h e   M P C   w i l l   o n l y   l o o k   a t   a n d   a t t e m p t   t o   o p t i m i z e   a   f e w   p o i n t s ,   b u t   t h e   p r e d i c t i o n   w i l l   b e   h i g h - f i 
                 x d e e r _ p r e d _ d o w n s a m p l e d   =   z e r o s ( ( s e l f . N p , 4 ) ) 
                 f o r   k   i n   r a n g e ( 0 , 4 ) : 
                         x d e e r _ p r e d _ d o w n s a m p l e d [ : , k ]   =   i n t e r p ( s e l f . t _ h o r i z o n , t v e c , x d e e r _ p r e d [ : , k ] ) 
                 r e t u r n   x d e e r _ p r e d _ d o w n s a m p l e d 
 
         d e f   p r e d i c t C a r ( s e l f , c a r n o w , x _ a c c e l v e c t o r ) : 
                 p r e d i c t C a r   =   c o p y . d e e p c o p y ( c a r n o w ) 
                 p r e d i c t C a r . t i r e t y p e = ' l i n e a r ' 
                 # c o m p u t e   t h e   n u m p e r   o f   t i m e s t e p s   w e   w i l l   s i m u l a t e   u s i n g   t h e   C A R ' s   d t 
                 t i m e s t e p s   =   s e l f . p r e d i c t i o n _ t i m e / p r e d i c t C a r . d T 
                 # c o m p u t e   a   t i m e   v e c t o r   f o r   p r e d i c t i n g 
                 t v e c   =   a r a n g e ( 0 , s e l f . p r e d i c t i o n _ t i m e + p r e d i c t C a r . d T , p r e d i c t C a r . d T ) 
                 # i n i t i a l i z e   t h e   d o w n s a m p l e d   v e c t o r   w e   w i l l   r e t u r n 
                 x c a r _ p r e d _ d o w n s a m p l e d   =   z e r o s ( ( s e l f . N p , 6 ) ) 
                 x d o t c a r _ p r e d _ d o w n s a m p l e d   =   z e r o s ( ( s e l f . N p , 6 ) ) 
                 # i n i t i a l i z e   t h e   ' f i n e '   v e c t o r   w e   w i l l   f i l l   w h i l e   p r e d i c t i n g   
                 x c a r _ p r e d   =   z e r o s ( ( l e n ( t v e c ) , 6 ) ) 
                 x d o t c a r _ p r e d     =   z e r o s ( ( l e n ( t v e c ) , 6 ) ) 
                 # w e   h a v e   t o   ' u p s a m p l e '   t h e   s t e e r   v e c t o r   s i n c e   i t   i s   o n l y   N p   l o n g .   i t   w i l l   l o o k   l i k e   ' s t a i r s ' 
                 x _ a c c e l v e c t o r _ u p s a m p l e d   =   i n t e r p ( t v e c , s e l f . t _ h o r i z o n , x _ a c c e l v e c t o r ) 
                 # p r i n t   s t e e r v e c t o r _ u p s a m p l e d . s h a p e 
                 # a c t u a l l y   p r e d i c t   t h e   c a r ' s   s t a t e s   g i v e n   t h e   i n p u t 
                 f o r   k   i n   r a n g e ( 0 , s e l f . N p ) : 
                         i f   x _ a c c e l v e c t o r _ u p s a m p l e d [ k ]   >   0 : 
                                 g a s   =   x _ a c c e l v e c t o r _ u p s a m p l e d [ k ] 
                                 b r a k e   =   0 
                                 x c a r _ p r e d [ k , : ] , x d o t c a r _ p r e d [ k , : ]   =   p r e d i c t C a r . h e u n s _ u p d a t e ( g a s   =   g a s ,   b r a k e   =   b r a k e ,   s t e e r   =   0 ,   c r u i s e   =   ' o f f ' ) 
                         e l s e : 
                                 g a s   =   0 
                                 b r a k e   =   a b s ( x _ a c c e l v e c t o r _ u p s a m p l e d [ k ] ) 
                                 x c a r _ p r e d [ k , : ] , x d o t c a r _ p r e d [ k , : ]   =   p r e d i c t C a r . h e u n s _ u p d a t e ( g a s   =   g a s ,   b r a k e   =   b r a k e ,   s t e e r   =   0 ,   c r u i s e   =   ' o f f ' ) 
                 # n o w   d o w n s a m p l e   t h e   p r e d i c t i o n   s o   i t   i s   o n l y   M P C . N p   p o i n t s   l o n g 
                 f o r   k   i n   r a n g e ( 0 , 6 ) : 
                         x c a r _ p r e d _ d o w n s a m p l e d [ : , k ]   =   i n t e r p ( s e l f . t _ h o r i z o n , t v e c , x c a r _ p r e d [ : , k ] ) 
                         x d o t c a r _ p r e d _ d o w n s a m p l e d [ : , k ]   =   i n t e r p ( s e l f . t _ h o r i z o n , t v e c , x d o t c a r _ p r e d [ : , k ] ) 
                 # p r i n t   x d o t c a r _ p r e d _ d o w n s a m p l e d . s h a p e , x c a r _ p r e d _ d o w n s a m p l e d . s h a p e 
                 r e t u r n   x c a r _ p r e d _ d o w n s a m p l e d , x d o t c a r _ p r e d _ d o w n s a m p l e d 
 
         d e f   O b j e c t i v e F n ( s e l f , x _ a c c e l v e c t o r , c a r n o w , d e e r n o w , s e t S p e e d ) : 
                 J = 0 
                 # N p   r o w s   b y   6   c o l u m n s ,   o n e   f o r   e a c h   s t a t e   ( o r   v i c e   v e r s a ) 
                 x c a r _ p r e d , x d o t c a r _ p r e d   =   s e l f . p r e d i c t C a r ( c a r n o w , x _ a c c e l v e c t o r ) 
                 x d e e r _ p r e d   =   s e l f . p r e d i c t D e e r _ s t a t i c ( d e e r n o w , c a r n o w ) 
 
                 # N p   r o w s   b y   5   c o l u m n s ,   o n e   f o r   x   a n d   y   o f   d e e r 
                 J   =   0   #   i n i t i a l i z e   t h e   o b j e c t i v e   t o   z e r o 
                 # n o w   l o o p   t h r o u g h   a n d   u p f d a t e   J   f o r   e v e r y   t i m e s t e p   i n   t h e   p r e d i c t i o n   h o r i z o n . 
                 f o r   k   i n   r a n g e ( 0 , s e l f . N p ) : 
                         d i s t a n c e   =   s q r t ( ( x c a r _ p r e d [ k , 0 ]   -   x d e e r _ p r e d [ k , 3 ] ) * * 2 +   ( x c a r _ p r e d [ k , 2 ]   -   x d e e r _ p r e d [ k , 2 ] ) * * 2 ) 
                         # r e t u r n   d i s t a n c e 
                         i f ( c a r n o w . x [ 2 ] < d e e r n o w . x _ D e e r ) : 
                                 J   =   J   +   s e l f . q _ x _ a c c e l   *   ( x _ a c c e l v e c t o r [ k ] ) * * 2   +   s e l f . q _ c r u i s e _ s p e e d   *   ( x c a r _ p r e d [ k , 3 ] - s e t S p e e d ) * * 2   +   s e l f . q _ o b s t a c l e _ e r r o r   *   ( 1 / ( d i s t a n c e + s e l f . e p s i l o n ) ) * * 2 
                         e l s e : 
                                 # p r i n t   " p a s s e d   d e e r ! " 
                                 J   =   J   +   s e l f . q _ c r u i s e _ s p e e d   *   ( x c a r _ p r e d [ k , 3 ] - s e t S p e e d ) * * 2 
                 r e t u r n   J 
 
 
         d e f   c a l c O p t i m a l ( s e l f , c a r n o w , d e e r n o w , s e t S p e e d ) : 
                 x _ a c c e l v e c t o r   =   0 . 5 * r a n d o m . r a n d n ( s e l f . N p ) 
 
                 b o u n d s   =   [ ( - s e l f . b r a k e _ m a x , s e l f . g a s _ m a x ) ] 
                 f o r   i n d   i n   r a n g e ( 1 , s e l f . N p ) : 
                         b o u n d s . i n s e r t ( 0 , ( - s e l f . b r a k e _ m a x , s e l f . g a s _ m a x ) ) 
 
                 u m p c   =   m i n i m i z e ( s e l f . O b j e c t i v e F n , x _ a c c e l v e c t o r , a r g s   =   ( c a r n o w , d e e r n o w , s e t S p e e d ) , b o u n d s   =   b o u n d s ,   m e t h o d   =   ' S L S Q P ' ) 
                 #   u m p c   =   m i n i m i z e ( s e l f . O b j e c t i v e F n , s t e e r v e c t o r , a r g s   =   ( c a r n o w , d e e r n o w , y r o a d ) , b o u n d s   =   b o u n d s ,   m e t h o d = ' B F G S ' , o p t i o n s = { ' x t o l ' :   1 e - 1 2 ,   ' d i s p ' :   F a l s e , ' e p s ' : . 0 0 0 1 , ' g t o l ' : . 0 0 0 1 } ) 
                 # m e t h o d = ' B F G S ' , o p t i o n s = { ' x t o l ' :   1 e - 1 2 ,   ' d i s p ' :   F a l s e , ' e p s ' : . 0 0 0 1 , ' g t o l ' : . 0 0 0 1 } 
                 o p t _ x _ a c c e l   =   u m p c . x [ 0 ] 
 
                 i f   ( o p t _ x _ a c c e l   >   0 ) :   
                         g a s   =   o p t _ x _ a c c e l 
                         b r a k e   =   0 
 
                 e l s e : 
                         g a s   =   0 
                         b r a k e   =   a b s ( o p t _ x _ a c c e l ) 
 
                 r e t u r n   g a s , b r a k e 
 
 d e f   d e m o ( ) : 
 
         x _ a c c e l d i s t a n c e   =   5 0 . 0 
         s e t S p e e d   =   2 5 . 0 
 
         d e e r _ i n d   =   ' 1 0 1 0 0 0 0 0 0 1 1 1 0 0 1 0 1 1 0 0 1 1 1 1 0 ' 
 
         d e e r _ i n d   =   B i n a r y C o n v e r s i o n ( d e e r _ i n d ) 
 
         d e e r   =   D e e r ( P s i 0 _ D e e r   =   d e e r _ i n d [ 0 ] ,   S i g m a _ P s i   =   d e e r _ i n d [ 1 ] ,   t t u r n _ D e e r   =   d e e r _ i n d [ 2 ] ,   V m a x _ D e e r   =   d e e r _ i n d [ 3 ] ,   T a u _ D e e r   =   d e e r _ i n d [ 4 ] ) 
 
         #   I n d i c a t e   d e e r   i n i t i a l   p o s i t i o n 
         d e e r . x _ D e e r   =   8 0 
         d e e r . y _ D e e r   =   0 # P U T   T H E   D E E R   I N   T H E   M I D D L E   O F   T H E   R O A D ! ! 
                 
         #   D e f i n e   s i m u l a t i o n   t i m e   a n d   d t 
         s i m t i m e   =   1 0 
         d t   =   d e e r . d T 
         t   =   a r a n g e ( 0 , s i m t i m e , d t )   # t a k e s   m i n ,   m a x ,   a n d   t i m e s t e p \ 
 
 
         c a r   =   B i c y c l e M o d e l ( d T   =   d t ,   U   =   2 5 . 0 , t i r e t y p e = ' p a c e j k a ' ) 
 
 
           # c a r   s t a t e   v e c t o r   # p r i n t   a r r a y ( [ [ Y d o t ] , [ v d o t ] , [ X d o t ] , [ U d o t ] , [ P s i d o t ] , [ r d o t ] ] ) 
         c a r x   =   z e r o s ( ( l e n ( t ) , l e n ( c a r . x ) ) ) 
         c a r x d o t   =   z e r o s ( ( l e n ( t ) , l e n ( c a r . x ) ) ) 
         c a r . x [ 3 ]   =   s e t S p e e d 
         c a r . x [ 0 ]   =   0 . 0   # l e t   t h e   v e h i c l e   s t a r t   a w a y   f r o m   l a n e . 
         c a r x [ 0 , : ]   =   c a r . x 
 
         # i n i t i a l i z e   f o r   d e e r   a s   w e l l 
         d e e r x   =   z e r o s ( ( l e n ( t ) , 4 ) ) 
         # f i l l   i n   i n i t i a l   c o n d i t i o n s   b e c a u s e   t h e y ' r e   n o n z e r o 
         d e e r x [ 0 , : ]   =   a r r a y ( [ d e e r . S p e e d _ D e e r , d e e r . P s i _ D e e r , d e e r . x _ D e e r , d e e r . y _ D e e r ] ) 
 
         M P C   =   M P C _ G ( q _ o b s t a c l e _ e r r o r   =   1 0 0 0 0 0 0 0 0 0 . 0 , q _ x _ a c c e l = 0 . 0 , q _ c r u i s e _ s p e e d = 0 . 0 1 , b r a k e _ m a x   =   0 . 5 ) 
 
 
         s t e e r v e c   =   z e r o s ( l e n ( t ) ) 
         a c c e l v e c   =   z e r o s ( l e n ( t ) ) 
         d i s t a n c e v e c   =   z e r o s ( l e n ( t ) ) 
         # n o w   s i m u l a t e ! ! 
         f o r   k   i n   r a n g e ( 1 , l e n ( t ) ) : 
 
                         # p r i n t   c a r x [ k - 1 , : ] 
                         # p r i n t   d e e r x [ k - 1 , : ] 
                         # a c c e l v e c   =   z e r o s ( 5 ) 
                         o p t _ s t e e r   =   0 
 
                         # M P C . O b j e c t i v e F n ( a c c e l v e c , c a r , d e e r , 2 5 . 0 ) 
                         # o p t _ x _ a c c e l   =   0 # 
                         g a s , b r a k e   =   M P C . c a l c O p t i m a l ( c a r n o w   =   c a r ,   d e e r n o w   =   d e e r ,   s e t S p e e d   =   s e t S p e e d ) 
 
                         i f   ( ( s q r t ( ( d e e r . x _ D e e r   -   c a r . x [ 2 ] ) * * 2 + ( d e e r . y _ D e e r   -   c a r . x [ 0 ] ) * * 2 )   <   x _ a c c e l d i s t a n c e )   a n d   ( d e e r . x _ D e e r > c a r . x [ 2 ] ) ) : 
 
                                 c a r x [ k , : ] , c a r x d o t [ k , : ]   =   c a r . h e u n s _ u p d a t e ( g a s   =   g a s ,   b r a k e   =   b r a k e ,   s t e e r   =   0 ,   c r u i s e   =   ' o f f ' ) 
                                 d e e r x [ k , : ]   =   a r r a y ( [ d e e r . S p e e d _ D e e r ,   d e e r . P s i _ D e e r ,   d e e r . x _ D e e r ,   d e e r . y _ D e e r ] ) # u p d a t e D e e r ( c a r . x [ 2 ] ) 
                                 d e e r x [ k , : ]   =   d e e r . u p d a t e D e e r ( c a r . x [ 2 ] ) 
                                 # s t e e r v e c [ k ]   =   o p t _ s t e e r 
                                 a c c e l v e c [ k ]   =   c a r x d o t [ k , 3 ] 
                                 p r i n t   " m p c   a c t i v e " 
 
                         e l s e : 
                                 c a r x [ k , : ] , c a r x d o t [ k , : ]   =   c a r . h e u n s _ u p d a t e ( s t e e r   =   0 ,   s e t s p e e d   =   s e t S p e e d , ) 
                                 # c a r x [ k , : ] , c a r x d o t [ k , : ]   =   c a r . h e u n s _ u p d a t e ( g a s   =   g a s ,   b r a k e   =   b r a k e ,   s t e e r   =   0 ,   c r u i s e   =   ' o f f ' ) 
                                 # d e e r x [ k , : ]   =   a r r a y ( [ d e e r . S p e e d _ D e e r ,   d e e r . P s i _ D e e r ,   d e e r . x _ D e e r ,   d e e r . y _ D e e r ] ) # u p d a t e D e e r ( c a r . x [ 2 ] ) 
                                 d e e r x [ k , : ]   =   d e e r . u p d a t e D e e r ( c a r . x [ 2 ] ) 
                                 # s t e e r v e c [ k ]   =   o p t _ s t e e r 
                                 a c c e l v e c [ k ]   =   c a r x d o t [ k , 3 ] 
 
                         d i s t a n c e v e c [ k ]   =   s q r t ( ( d e e r . x _ D e e r   -   c a r . x [ 2 ] ) * * 2 + ( d e e r . y _ D e e r   -   c a r . x [ 0 ] ) * * 2 ) 
                         p r i n t   r o u n d ( t [ k ] , 2 ) , r o u n d ( g a s , 2 ) , r o u n d ( b r a k e , 2 ) 
 
         a y g   =   ( c a r x d o t [ : , 1 ] + c a r x [ : , 5 ] * c a r x [ : , 3 ] ) / 9 . 8 1 
         
         f i g u r e ( ) 
         p l o t ( t , s t e e r v e c , ' k ' ) 
         x l a b e l ( ' T i m e   ( s ) ' ) 
         y l a b e l ( ' s t e e r   a n g l e   ( r a d ) ' ) 
         f i g u r e ( ) 
         p l o t ( t , c a r x [ : , 0 ] , ' k ' ) 
         x l a b e l ( ' T i m e   ( s ) ' ) 
         y l a b e l ( ' c a r   Y   p o s i t i o n   ( m ) ' ) 
         f i g u r e ( ) 
         p l o t ( t , a y g , ' k ' ) 
         x l a b e l ( ' t i m e   ( s ) ' ) 
         y l a b e l ( ' l a t e r a l   a c c e l e r a t i o n   ( g ) ' ) 
         f i g u r e ( ) 
         p l o t ( t , c a r x [ : , 3 ] , ' k ' ) 
         x l a b e l ( ' T i m e   ( s ) ' ) 
         y l a b e l ( ' c a r   f o r w a r d   v e l o c i t y   ( m / s ) ' ) 
         f i g u r e ( ) 
         p l o t ( c a r x [ : , 2 ] , c a r x [ : , 0 ] , ' k ' , d e e r x [ : , 2 ] , d e e r x [ : , 3 ] , ' r o ' ) 
         a x i s ( ' e q u a l ' ) 
         x l a b e l ( ' X   ( m ) ' ) 
         y l a b e l ( ' Y   ( m ) ' ) 
         l e g e n d ( [ ' c a r ' , ' d e e r ' ] ) 
         f i g u r e ( ) 
         p l o t ( t , a c c e l v e c , ' k ' ) 
         x l a b e l ( ' t i m e   ( s ) ' ) 
         y l a b e l ( ' l o n g i t u d i n a l   a c c e l e r a t i o n   ( m / s / s ) ' ) 
         f i g u r e ( ) 
         p l o t ( t , d i s t a n c e v e c , ' k ' ) 
         x l a b e l ( ' t i m e   ( s ) ' ) 
         y l a b e l ( ' c a r - d e e r   d i s t a n c e   ( m ) ' ) 
         s h o w ( ) 
 
 
 i f   _ _ n a m e _ _   = =   ' _ _ m a i n _ _ ' : 
         d e m o ( ) 