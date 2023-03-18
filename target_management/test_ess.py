import unittest
from .ess_controller import EssApiController
from django.conf import settings
from rest_framework import status
import json
from rest_framework.response import  Response


class testesscontroller(unittest.TestCase):
    def setUp(self):
       pass
    def tearDown(self):
       pass 

    def test_ess_add_smart_search_target(self):
           obj1=EssApiController()
           response_recieved=obj1.ess_add_smart_search_target()
           response_expected={'data':{'full_name': 'Arooma Shah', 'id': '100002564297734', 'profile_image_url': '', 'url': 'https://www.facebook.com/arooma.shah', 'username': 'arooma.shah'}}
           micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
           if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)  
           elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)     
           else:
                self.assertEqual(response_recieved,response_expected )
       
      

    def test_add_target(self):
      
            obj1=EssApiController()
            response_recieved=obj1.add_target( 'muneeb', 'facebook', 'profile', 'st_in_457', '0', 10)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)    
            
            else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
            

   
    def test_instagram_target_identification(self):
        
            obj1=EssApiController()
            response_recieved=obj1.instagram_target_identification('muneeb')
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            response_expected={'data':'shams'}
            print(response_expected) 
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)    
            
            else:
                self.assertEqual(response_recieved,response_expected )
            
      
        
    def test_facebook_target_identification(self):

            obj1=EssApiController()
            response_recieved=obj1.facebook_target_identification('muneeb.malik.3158')
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            response_expected={'entity_type': 'users', 'full_name': 'Muneeb Malik', 'id': '', 'image': 'https://scontent.fisb1-1.fna.fbcdn.net/v/t1.6435-1/cp0/p60x60/119460683_2737521326519392_6925211146300705207_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=7206a8&_nc_ohc=FQ8agn7cPq0AX_CRdMG&_nc_ht=scontent.fisb1-1.fna&tp=27&oh=84b8d2855d534020b9e70ba8a9f731fb&oe=60A80C45', 'picture_url': 'https://scontent.fisb1-1.fna.fbcdn.net/v/t1.6435-1/cp0/p60x60/119460683_2737521326519392_6925211146300705207_n.jpg?_nc_cat=105&ccb=1-3&_nc_sid=7206a8&_nc_ohc=FQ8agn7cPq0AX_CRdMG&_nc_ht=scontent.fisb1-1.fna&tp=27&oh=84b8d2855d534020b9e70ba8a9f731fb&oe=60A80C45', 'url': 'https://www.facebook.com/muneeb.malik.3158', 'username': 'muneeb.malik.3158'}
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)    
            else:
                response_recieved=response_recieved['data']['data'][0]
                print(response_recieved)
                self.assertEqual(response_recieved,response_expected )
         
    def test_twitter_target_identification(self):
    
           obj1=EssApiController()
           response_recieved=obj1.twitter_target_identification('shamsuddinsyed5')
           # print(response_recieved)
           micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
           response_expected={'data': {'data': [{'full_name': 'Syed Shamsuddin', 'id': '870755049617620993', 'picture_url': 'https://pbs.twimg.com/profile_images/1087647235746209792/cXVr6Wm5_normal.jpg', 'username': 'Shamsuddinsyed5'}], 'site': 'twitter'}}
           if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)

           elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)
           else:
                print(response_recieved)
                self.assertEqual(response_recieved,response_expected )
    
    def test_reddit_target_identification(self):
            obj1=EssApiController()
            response_recieved=obj1.reddit_target_identification('u/pewpewpewPEWdie')
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            response_expected=bool(response_recieved)
            if response_recieved==micro_crwaler_error:
                print('test failed')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                self.assertNotEqual(response_recieved,None)     
            else:
                self.assertTrue(response_expected)
         


    def test_dark_web_search(self):
       
    
            obj1=EssApiController()
            response_recieved=obj1.dark_web_search('imran khan')
            # response_expected={'description': 'Imran Khan - BBC NewsAll the latest news about Imran Khan from the BBC Homepage Accessibility links Skip to content Accessibility Help BBC Account Notifications Home News Sport Weather iPlayer', 'link': 'https://www.s5rhoqqosmcispfb.onion/news/topics/c514kvxgnx8t/imran-khan', 'score': 1, 'title': 'Imran Khan - BBC News'}
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('test failed')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                self.assertNotEqual(response_recieved,None)     
            else:
                # response_recieved=response_recieved['data'][0]
                # self.assertEqual(response_recieved,response_expected )
                print('test result :')
                self.assertTrue(response_expected)
         
    def test_google_scholar_data_scraper(self):

            obj1=EssApiController()
            response_recieved=obj1.google_scholar_data_scraper('S Keyvaninia')
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}        
            response_expected={'data': [{'citations': '241', 'link': 'https://ieeexplore.ieee.org/abstract/document/6697878/', 'partial_summary': 'This paper summarizes recent advances of integrated hybrid InP/SOI lasers and transmitters based on wafer bonding. At first the integration process of III-V materials on silicon is described. Then the paper reports on the results of single wavelength distributed Bragg\xa0…', 'pdf': {'link': 'https://eprints.soton.ac.uk/368064/1/JSTQE_laser_Final.pdf', 'site': ' soton.ac.uk'}, 'publish_data': {'authors': '…, G de Valicourt, S Keyvaninia…\xa0- IEEE Journal of\xa0…, 2014', 'journal/conference': 'ieeexplore.ieee.org', 'site': ''}, 'title': 'Hybrid III--V on Silicon Lasers for Photonic Integrated Circuits on Silicon', 'versions': '17'}]}
            x=set(response_expected).issubset(set(response_recieved))
            if response_recieved==micro_crwaler_error:
                print('test failed')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                self.assertNotEqual(response_recieved,None)    
            else:
                self.assertTrue(x)

    def test_google_patents_data_scraper(self):
            obj1=EssApiController()
            response_recieved=obj1.google_patents_data_scraper('imran khan')
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            response_expected=bool(response_recieved)
            if response_recieved==micro_crwaler_error:
                print('test failed')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                self.assertNotEqual(response_recieved,None)    
            else:
                self.assertTrue(response_expected)


    
    def test_amazon_data_scraper(self):
            obj1=EssApiController()
            response_recieved=obj1.amazon_data_scraper('muneeb')
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;(: (Scrapping with Respect) ;('}
            response_expected=bool(response_recieved)
            response_expected={}
            if response_recieved==micro_crwaler_error:
                print('test failed')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)    
            else:
                self.assertTrue(response_expected)
      
         
    def test_tweets_search_result(self): 
            obj1=EssApiController()
            response_recieved=obj1.tweets_search_result('people','zayn','songs','gigi','haryy','music','english',1,1,1)
            print(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            response_expected=bool(response_recieved)
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)      
            else:
                self.assertTrue(response_expected )
         


    # def test_create_payload(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.create_payload('url')
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         response_expected=bool(response_recieved)
    #         if response_recieved==micro_crwaler_error:
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #            self.assertNotEqual(response_recieved,None)      
    #         else:
    #             self.assertTrue(response_expected )

    # def test_image_reverse_lookup(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.image_reverse_lookup('image','url')
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         response_expected=bool(response_recieved)
    #         if response_recieved==micro_crwaler_error:
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #            self.assertNotEqual(response_recieved,None)      
    #         else:
    #             self.assertTrue(response_expected )

    
    def test_get_domains_ip_info(self): 
            obj1=EssApiController()
            response_recieved=obj1.get_domains_ip_info()
            print(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            response_expected=bool(response_recieved)
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)      
            else:
                self.assertTrue(response_expected )


    def test_get_domains_info(self): 
            obj1=EssApiController()
            response_recieved=obj1.get_domains_info()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)      
            else:
                self.assertTrue(response_expected)

    # def test_track_ip(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.track_ip('code')
    #         response_expected=bool(response_recieved)
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         if response_recieved==micro_crwaler_error:
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #            self.assertNotEqual(response_recieved,None)      
    #         else:
    #             self.assertTrue(response_expected)
                
    # def test_get_tag_originator(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.get_tag_originator('tagName')
    #         response_expected=bool(response_recieved)
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         if response_recieved==micro_crwaler_error:
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #            self.assertNotEqual(response_recieved,None)      
    #         else:
    #             self.assertTrue(response_expected)

    def test_ess_add_twitter_trends_worldwide_target(self): 
            obj1=EssApiController()
            response_recieved=obj1.ess_add_twitter_trends_worldwide_target()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)      
            else:
                self.assertTrue(response_expected)
    def test_twitter_trends(self): 
            obj1=EssApiController()
            response_recieved=obj1.twitter_trends('pakistan')
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)      
            else:
                self.assertTrue(response_expected)  
    def test_youtube_trends(self): 
            obj1=EssApiController()
            response_recieved=obj1.youtube_trends()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)      
            else:
                self.assertTrue(response_expected)  
                          
    def test_reddit_trends(self): 
            obj1=EssApiController()
            response_recieved=obj1.reddit_trends()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print('test result ')
                self.assertTrue(response_expected)  
                          
    def test_microcrawler_status(self): 
            obj1=EssApiController()
            response_recieved=obj1.microcrawler_status()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print('test result')
                self.assertTrue(response_expected)  
                          
    def test_crawler_internet_connection(self): 
            obj1=EssApiController()
            response_recieved=obj1.microcrawler_status()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print('test result')
                self.assertTrue(response_expected)  
                                                                                                                                
    def test_ess_add_news_target(self): 
            obj1=EssApiController()
            response_recieved=obj1.ess_add_news_target()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                self.assertTrue(response_expected)   

                                                                                                                                
    def test_get_news_search(self): 
            obj1=EssApiController()
            response_recieved=obj1.get_news_search('weather')
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                self.assertTrue(response_expected)   

   
    def test_news_crawling(self): 
            obj1=EssApiController()
            response_recieved=obj1.news_crawling()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                print(response_recieved)
                self.assertTrue(response_expected)             

    def test_news_crawling(self): 
            obj1=EssApiController()
            response_recieved=obj1.news_crawling()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                print(response_recieved)
                self.assertTrue(response_expected)             
            
    def test_action_post(self): 
            obj1=EssApiController()
            response_recieved=obj1.action_post('hi morning','tw','malikmuneeb1998m','cypher@12345')
            # response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
                # print(' test result')
                # print(response_recieved)
                # self.assertTrue(response_expected)      

    def test_action_comment(self): 
            obj1=EssApiController()
            response_recieved=obj1.action_comment('hi how are you all doing','https://twitter.com/Shamsuddinsyed5/status/1045378223465549825?ref_src=twsrc%5Etfw','tw','muneeb28061305','cypher@12345')
            # response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
                # print(response_recieved)
                # self.assertTrue(response_expected)             
                        

    def test_action_reaction(self): 
            obj1=EssApiController()
            response_recieved=obj1.action_reaction('reaction','https://twitter.com/Shamsuddinsyed5/status/1045378223465549825?ref_src=twsrc%5Etfw','tw','muneeb28061305','cypher@12345')
            # response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
                # print(' test result')
                # print(response_recieved)
                # self.assertTrue(response_expected)      
                      
    def test_action_share(self): 
            obj1=EssApiController()
            response_recieved=obj1.action_share('heyyyyyy dumbo','https://twitter.com/Shamsuddinsyed5/status/1045378223465549825?ref_src=twsrc%5Etfw','tw','muneeb28061305','cypher@12345')
            # response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
                # print(' test result')
                # print(response_recieved)
                # self.assertTrue(response_expected)                        
                                                   
    def test_action_send_message(self): 
            obj1=EssApiController()
            response_recieved=obj1.action_send_message('tw','Shamsuddinsyed5','hi')
            # response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
                # print(' test result')
                # print(response_recieved)
                # self.assertTrue(response_expected)      
                      
    def test_getall_sm_account(self): 
            obj1=EssApiController()
            response_recieved=obj1.getall_sm_account()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                print(response_recieved)
                self.assertTrue(response_expected) 
                           
    def test_add_sm_account(self): 
            obj1=EssApiController()
            response_recieved=obj1.add_sm_account("tw", "muneeb28061305", "1", "malikmuneeb1998m@gmail.com", "cypher@12345", "12")
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                print(response_recieved)
                self.assertTrue(response_expected)                        
    # def test_update_sm_account(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.update_sm_account("social_media", "username", "status", "email", "password", "userid")
    #         response_expected=bool(response_recieved)
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         if response_recieved==micro_crwaler_error:
    #             print('issue at micro crawler end')
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #             print('nothing recieved')
    #             self.assertNotEqual(response_recieved,None)      
    #         else:
    #             print(' test result')
    #             print(response_recieved)
    # #             self.assertTrue(response_expected)                        

    # def test_delete_sm_account(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.delete_sm_account("userid")
    #         response_expected=bool(response_recieved)
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         if response_recieved==micro_crwaler_error:
    #             print('issue at micro crawler end')
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #             print('nothing recieved')
    #             self.assertNotEqual(response_recieved,None)      
    #         else:
    #             print(' test result')
    #             print(response_recieved)
    #             self.assertTrue(response_expected)                        
                                                                                                                                                                                                                                                                                                       
    # def test_get_task_terminate(self): 
    #         obj1=EssApiController()
    #         response_recieved=obj1.get_task_terminate("1")
    #         response_expected=bool(response_recieved)
    #         micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
    #         if response_recieved==micro_crwaler_error:
    #             print('issue at micro crawler end')
    #             self.assertNotEqual(response_recieved,micro_crwaler_error)
    #         elif response_recieved==None:
    #             print('nothing recieved')
    #             self.assertNotEqual(response_recieved,None)      
    #         else:
    #             print(' test result')
    #             print(response_recieved)
    #             self.assertTrue(response_expected)                        
    
    def test_get_crawler_status(self): 
            obj1=EssApiController()
            response_recieved=obj1.get_crawler_status()
            response_expected=bool(response_recieved)
            micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
            if response_recieved==micro_crwaler_error:
                print('issue at micro crawler end')
                self.assertNotEqual(response_recieved,micro_crwaler_error)
            elif response_recieved==None:
                print('nothing recieved')
                self.assertNotEqual(response_recieved,None)      
            else:
                print(' test result')
                print(response_recieved)
                self.assertTrue(response_expected)          



    def test_dynamic_crawling(self):
           obj1=EssApiController()
           response_recieved=obj1.dynamic_crawling('https://www.facebook.com/arooma.shah',True,True,True,True,True,True,True,'st_in_457','0')
           response_expected=bool(response_recieved)
           micro_crwaler_error={'code': 0, 'message': 'Got Exception From Micro-Crawler: (Scrapping with Respect) ;('}
           if response_recieved==micro_crwaler_error:
                self.assertNotEqual(response_recieved,micro_crwaler_error)  
           elif response_recieved==None:
               self.assertNotEqual(response_recieved,None)     
           else:
                response_expected=response_recieved['status']
                self.assertEqual(response_expected,200 )
                                                             
        
if __name__ =='__main__':
    unittest.main()       














