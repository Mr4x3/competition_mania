# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-03 18:49
from __future__ import unicode_literals

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_on', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('unread', models.BooleanField(default=True)),
                ('deleted_by_sender', models.BooleanField(default=False)),
                ('deleted_by_recipient', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1)),
                ('mobile', models.CharField(blank=True, max_length=10)),
                ('country', models.CharField(choices=[('AF', 'Afghanistan'), ('AX', 'Aland Islands'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BQ', 'Bonaire, Saint Eustatius and Saba '), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('VG', 'British Virgin Islands'), ('BN', 'Brunei'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Curacao'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('CD', 'Democratic Republic of the Congo'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('TL', 'East Timor'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('CI', 'Ivory Coast'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', 'Laos'), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia'), ('MD', 'Moldova'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('KP', 'North Korea'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestinian Territory'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('CG', 'Republic of the Congo'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RU', 'Russia'), ('RW', 'Rwanda'), ('BL', 'Saint Barthelemy'), ('SH', 'Saint Helena'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('KR', 'South Korea'), ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syria'), ('TW', 'Taiwan'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania'), ('TH', 'Thailand'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('VI', 'U.S. Virgin Islands'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VA', 'Vatican'), ('VE', 'Venezuela'), ('VN', 'Vietnam'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')], default='IN', max_length=2)),
                ('state', models.IntegerField(blank=True, choices=[(1001, 'Andaman and Nicobar Island'), (1002, 'Andhra Pradesh'), (1003, 'Arunachal Pradesh'), (1004, 'Assam'), (1005, 'Bihar'), (1006, 'Chandigarh'), (1007, 'Chhattisgarh'), (1008, 'Dadra and Nagar Haveli'), (1009, 'Daman and Diu'), (1010, 'Delhi'), (1011, 'Goa'), (1012, 'Gujarat'), (1013, 'Haryana'), (1014, 'Himachal Pradesh'), (1015, 'Jammu and Kashmir'), (1016, 'Jharkhand'), (1017, 'Karnataka'), (1018, 'Kerala'), (1019, 'Lakshadweep'), (1020, 'Madhya Pradesh'), (1021, 'Maharashtra'), (1022, 'Manipur'), (1023, 'Meghalaya'), (1024, 'Mizoram'), (1025, 'Nagaland'), (1026, 'Odisha'), (1027, 'Puducherry'), (1028, 'Punjab'), (1029, 'Rajasthan'), (1030, 'Sikkim'), (1031, 'Tamil Nadu'), (1032, 'Telangana'), (1033, 'Tripura'), (1034, 'Uttar Pradesh'), (1035, 'Uttarakhand'), (1036, 'West Bengal')], null=True)),
                ('state_text', models.CharField(blank=True, max_length=30)),
                ('city', models.IntegerField(blank=True, choices=[(10001, 'Nicobar'), (10002, 'North and Middle Andaman'), (10003, 'South Andaman'), (10004, 'Anantapur'), (10005, 'Chittoor'), (10006, 'Cuddapah'), (10007, 'East Godavari'), (10008, 'Guntur'), (10009, 'Krishna'), (10010, 'Kurnool'), (10011, 'Nellore'), (10012, 'Prakasam'), (10013, 'Srikakulam'), (10014, 'Visakhapatnam'), (10015, 'Vizianagaram'), (10016, 'West Godavari'), (10017, 'Anjaw'), (10018, 'Changlang'), (10019, 'Dibang Valley'), (10020, 'East Kameng'), (10021, 'East Siang'), (10022, 'Kurung Kumey'), (10023, 'Lohit'), (10024, 'Longding'), (10025, 'Lower Dibang Valley'), (10026, 'Lower Subansiri'), (10027, 'Papum Pare'), (10028, 'Tawang'), (10029, 'Tirap'), (10030, 'Upper Siang'), (10031, 'Upper Subansiri'), (10032, 'West Kameng'), (10033, 'West Siang'), (10034, 'Baksa'), (10035, 'Barpeta'), (10036, 'Bongaigaon'), (10037, 'Cachar'), (10038, 'Chirang'), (10039, 'Darrang'), (10040, 'Dhemaji'), (10041, 'Dhubri'), (10042, 'Dibrugarh'), (10043, 'Dima Hasao'), (10044, 'Goalpara'), (10045, 'Golaghat'), (10046, 'Hailakandi'), (10047, 'Jorhat'), (10048, 'Kamrup Metropolitan'), (10049, 'Kamrup'), (10050, 'Karbi Anglong'), (10051, 'Karimganj'), (10052, 'Kokrajhar'), (10053, 'Lakhimpur'), (10054, 'Morigaon'), (10055, 'Nagaon'), (10056, 'Nalbari'), (10057, 'Sivasagar'), (10058, 'Sonitpur'), (10059, 'Tinsukia'), (10060, 'Udalguri'), (10061, 'Araria'), (10062, 'Arwal'), (10063, 'Aurangabad'), (10064, 'Banka'), (10065, 'Begusarai'), (10066, 'Bhagalpur'), (10067, 'Bhojpur'), (10068, 'Buxar'), (10069, 'Darbhanga'), (10070, 'East Champaran (Motihari)'), (10071, 'Gaya'), (10072, 'Gopalganj'), (10073, 'Jamui'), (10074, 'Jehanabad'), (10075, 'Kaimur (Bhabua)'), (10076, 'Katihar'), (10077, 'Khagaria'), (10078, 'Kishanganj'), (10079, 'Lakhisarai'), (10080, 'Madhepura'), (10081, 'Madhubani'), (10082, 'Munger (Monghyr)'), (10083, 'Muzaffarpur'), (10084, 'Nalanda'), (10085, 'Nawada'), (10086, 'Patna'), (10087, 'Purnia (Purnea)'), (10088, 'Rohtas'), (10089, 'Saharsa'), (10090, 'Samastipur'), (10091, 'Saran'), (10092, 'Sheikhpura'), (10093, 'Sheohar'), (10094, 'Sitamarhi'), (10095, 'Siwan'), (10096, 'Supaul'), (10097, 'Vaishali'), (10098, 'West Champaran'), (10099, 'Chandigarh'), (10100, 'Balod'), (10101, 'Baloda Bazar'), (10102, 'Balrampur'), (10103, 'Bastar'), (10104, 'Bemetara'), (10105, 'Bijapur'), (10106, 'Bilaspur'), (10107, 'Dantewada (South Bastar)'), (10108, 'Dhamtari'), (10109, 'Durg'), (10110, 'Gariaband'), (10111, 'Janjgir-Champa'), (10112, 'Jashpur'), (10113, 'Kabirdham (Kawardha)'), (10114, 'Kanker (North Bastar)'), (10115, 'Kondagaon'), (10116, 'Korba'), (10117, 'Korea (Koriya)'), (10118, 'Mahasamund'), (10119, 'Mungeli'), (10120, 'Narayanpur'), (10121, 'Raigarh'), (10122, 'Raipur'), (10123, 'Rajnandgaon'), (10124, 'Sukma'), (10125, 'Surajpur'), (10126, 'Surguja'), (10127, 'Dadra & Nagar Haveli'), (10128, 'Daman'), (10129, 'Diu'), (10130, 'Central Delhi'), (10131, 'East Delhi'), (10132, 'New Delhi'), (10133, 'North Delhi'), (10134, 'North East Delhi'), (10135, 'North West Delhi'), (10136, 'South Delhi'), (10137, 'South West Delhi'), (10138, 'West Delhi'), (10139, 'North Goa'), (10140, 'South Goa'), (10141, 'Ahmedabad'), (10142, 'Amreli'), (10143, 'Anand'), (10144, 'Aravalli'), (10145, 'Banaskantha (Palanpur)'), (10146, 'Bharuch'), (10147, 'Bhavnagar'), (10148, 'Botad'), (10149, 'Chhota Udepur'), (10150, 'Dahod'), (10151, 'Dangs (Ahwa)'), (10152, 'Devbhoomi Dwarka'), (10153, 'Gandhinagar'), (10154, 'Gir Somnath'), (10155, 'Jamnagar'), (10156, 'Junagadh'), (10157, 'Kachchh'), (10158, 'Kheda (Nadiad)'), (10159, 'Mahisagar'), (10160, 'Mehsana'), (10161, 'Morbi'), (10162, 'Narmada (Rajpipla)'), (10163, 'Navsari'), (10164, 'Panchmahal (Godhra)'), (10165, 'Patan'), (10166, 'Porbandar'), (10167, 'Rajkot'), (10168, 'Sabarkantha (Himmatnagar)'), (10169, 'Surat'), (10170, 'Surendranagar'), (10171, 'Tapi (Vyara)'), (10172, 'Vadodara'), (10173, 'Valsad'), (10174, 'Ambala'), (10175, 'Bhiwani'), (10176, 'Faridabad'), (10177, 'Fatehabad'), (10178, 'Gurgaon'), (10179, 'Hisar'), (10180, 'Jhajjar'), (10181, 'Jind'), (10182, 'Kaithal'), (10183, 'Karnal'), (10184, 'Kurukshetra'), (10185, 'Mahendragarh'), (10186, 'Mewat'), (10187, 'Palwal'), (10188, 'Panchkula'), (10189, 'Panipat'), (10190, 'Rewari'), (10191, 'Rohtak'), (10192, 'Sirsa'), (10193, 'Sonipat'), (10194, 'Yamunanagar'), (10195, 'Bilaspur'), (10196, 'Chamba'), (10197, 'Hamirpur'), (10198, 'Kangra'), (10199, 'Kinnaur'), (10200, 'Kullu'), (10201, 'Lahaul & Spiti'), (10202, 'Mandi'), (10203, 'Shimla'), (10204, 'Sirmaur (Sirmour)'), (10205, 'Solan'), (10206, 'Una'), (10207, 'Anantnag'), (10208, 'Bandipora'), (10209, 'Baramulla'), (10210, 'Budgam'), (10211, 'Doda'), (10212, 'Ganderbal'), (10213, 'Jammu'), (10214, 'Kargil'), (10215, 'Kathua'), (10216, 'Kishtwar'), (10217, 'Kulgam'), (10218, 'Kupwara'), (10219, 'Leh'), (10220, 'Poonch'), (10221, 'Pulwama'), (10222, 'Rajouri'), (10223, 'Ramban'), (10224, 'Reasi'), (10225, 'Samba'), (10226, 'Shopian'), (10227, 'Srinagar'), (10228, 'Udhampur'), (10229, 'Bokaro'), (10230, 'Chatra'), (10231, 'Deoghar'), (10232, 'Dhanbad'), (10233, 'Dumka'), (10234, 'East Singhbhum'), (10235, 'Garhwa'), (10236, 'Giridih'), (10237, 'Godda'), (10238, 'Gumla'), (10239, 'Hazaribag'), (10240, 'Jamtara'), (10241, 'Khunti'), (10242, 'Koderma'), (10243, 'Latehar'), (10244, 'Lohardaga'), (10245, 'Pakur'), (10246, 'Palamu'), (10247, 'Ramgarh'), (10248, 'Ranchi'), (10249, 'Sahibganj'), (10250, 'Seraikela-Kharsawan'), (10251, 'Simdega'), (10252, 'West Singhbhum'), (10253, 'Bagalkot'), (10254, 'Bangalore Rural'), (10255, 'Bangalore Urban'), (10256, 'Belgaum'), (10257, 'Bellary'), (10258, 'Bidar'), (10259, 'Bijapur'), (10260, 'Chamarajanagar'), (10261, 'Chickmagalur'), (10262, 'Chikballapur'), (10263, 'Chitradurga'), (10264, 'Dakshina Kannada'), (10265, 'Davangere'), (10266, 'Dharwad'), (10267, 'Gadag'), (10268, 'Gulbarga'), (10269, 'Hassan'), (10270, 'Haveri'), (10271, 'Kodagu'), (10272, 'Kolar'), (10273, 'Koppal'), (10274, 'Mandya'), (10275, 'Mysore'), (10276, 'Raichur'), (10277, 'Ramnagara'), (10278, 'Shimoga'), (10279, 'Tumkur'), (10280, 'Udupi'), (10281, 'Uttara Kannada (Karwar)'), (10282, 'Yadgir'), (10283, 'Alappuzha'), (10284, 'Ernakulam'), (10285, 'Idukki'), (10286, 'Kannur'), (10287, 'Kasaragod'), (10288, 'Kollam'), (10289, 'Kottayam'), (10290, 'Kozhikode'), (10291, 'Malappuram'), (10292, 'Palakkad'), (10293, 'Pathanamthitta'), (10294, 'Thiruvananthapuram'), (10295, 'Thrissur'), (10296, 'Wayanad'), (10297, 'Lakshadweep'), (10298, 'Alirajpur'), (10299, 'Anuppur'), (10300, 'Ashoknagar'), (10301, 'Balaghat'), (10302, 'Barwani'), (10303, 'Betul'), (10304, 'Bhind'), (10305, 'Bhopal'), (10306, 'Burhanpur'), (10307, 'Chhatarpur'), (10308, 'Chhindwara'), (10309, 'Damoh'), (10310, 'Datia'), (10311, 'Dewas'), (10312, 'Dhar'), (10313, 'Dindori'), (10314, 'Guna'), (10315, 'Gwalior'), (10316, 'Harda'), (10317, 'Hoshangabad'), (10318, 'Indore'), (10319, 'Jabalpur'), (10320, 'Jhabua'), (10321, 'Katni'), (10322, 'Khandwa'), (10323, 'Khargone'), (10324, 'Mandla'), (10325, 'Mandsaur'), (10326, 'Morena'), (10327, 'Narsinghpur'), (10328, 'Neemuch'), (10329, 'Panna'), (10330, 'Raisen'), (10331, 'Rajgarh'), (10332, 'Ratlam'), (10333, 'Rewa'), (10334, 'Sagar'), (10335, 'Satna'), (10336, 'Sehore'), (10337, 'Seoni'), (10338, 'Shahdol'), (10339, 'Shajapur'), (10340, 'Sheopur'), (10341, 'Shivpuri'), (10342, 'Sidhi'), (10343, 'Singrauli'), (10344, 'Tikamgarh'), (10345, 'Ujjain'), (10346, 'Umaria'), (10347, 'Vidisha'), (10348, 'Ahmednagar'), (10349, 'Akola'), (10350, 'Amravati'), (10351, 'Aurangabad'), (10352, 'Beed'), (10353, 'Bhandara'), (10354, 'Buldhana'), (10355, 'Chandrapur'), (10356, 'Dhule'), (10357, 'Gadchiroli'), (10358, 'Gondia'), (10359, 'Hingoli'), (10360, 'Jalgaon'), (10361, 'Jalna'), (10362, 'Kolhapur'), (10363, 'Latur'), (10364, 'Mumbai City'), (10365, 'Mumbai Suburban'), (10366, 'Nagpur'), (10367, 'Nanded'), (10368, 'Nandurbar'), (10369, 'Nashik'), (10370, 'Osmanabad'), (10371, 'Parbhani'), (10372, 'Pune'), (10373, 'Raigad'), (10374, 'Ratnagiri'), (10375, 'Sangli'), (10376, 'Satara'), (10377, 'Sindhudurg'), (10378, 'Solapur'), (10379, 'Thane'), (10380, 'Wardha'), (10381, 'Washim'), (10382, 'Yavatmal'), (10383, 'Bishnupur'), (10384, 'Chandel'), (10385, 'Churachandpur'), (10386, 'Imphal East'), (10387, 'Imphal West'), (10388, 'Senapati'), (10389, 'Tamenglong'), (10390, 'Thoubal'), (10391, 'Ukhrul'), (10392, 'East Garo Hills'), (10393, 'East Jaintia Hills'), (10394, 'East Khasi Hills'), (10395, 'North Garo Hills'), (10396, 'Ri Bhoi'), (10397, 'South Garo Hills'), (10398, 'South West Garo Hills'), (10399, 'South West Khasi Hills'), (10400, 'West Garo Hills'), (10401, 'West Jaintia Hills'), (10402, 'West Khasi Hills'), (10403, 'Aizawl'), (10404, 'Champhai'), (10405, 'Kolasib'), (10406, 'Lawngtlai'), (10407, 'Lunglei'), (10408, 'Mamit'), (10409, 'Saiha'), (10410, 'Serchhip'), (10411, 'Dimapur'), (10412, 'Kiphire'), (10413, 'Kohima'), (10414, 'Longleng'), (10415, 'Mokokchung'), (10416, 'Mon'), (10417, 'Peren'), (10418, 'Phek'), (10419, 'Tuensang'), (10420, 'Wokha'), (10421, 'Zunheboto'), (10422, 'Angul'), (10423, 'Balangir'), (10424, 'Balasore'), (10425, 'Bargarh'), (10426, 'Bhadrak'), (10427, 'Boudh'), (10428, 'Cuttack'), (10429, 'Deogarh'), (10430, 'Dhenkanal'), (10431, 'Gajapati'), (10432, 'Ganjam'), (10433, 'Jagatsinghapur'), (10434, 'Jajpur'), (10435, 'Jharsuguda'), (10436, 'Kalahandi'), (10437, 'Kandhamal'), (10438, 'Kendrapara'), (10439, 'Kendujhar (Keonjhar)'), (10440, 'Khordha'), (10441, 'Koraput'), (10442, 'Malkangiri'), (10443, 'Mayurbhanj'), (10444, 'Nabarangpur'), (10445, 'Nayagarh'), (10446, 'Nuapada'), (10447, 'Puri'), (10448, 'Rayagada'), (10449, 'Sambalpur'), (10450, 'Sonepur'), (10451, 'Sundargarh'), (10452, 'Karaikal'), (10453, 'Mahe'), (10454, 'Pondicherry'), (10455, 'Yanam'), (10456, 'Amritsar'), (10457, 'Barnala'), (10458, 'Bathinda'), (10459, 'Faridkot'), (10460, 'Fatehgarh Sahib'), (10461, 'Fazilka'), (10462, 'Ferozepur'), (10463, 'Gurdaspur'), (10464, 'Hoshiarpur'), (10465, 'Jalandhar'), (10466, 'Kapurthala'), (10467, 'Ludhiana'), (10468, 'Mansa'), (10469, 'Moga'), (10470, 'Muktsar'), (10471, 'Nawanshahr'), (10472, 'Pathankot'), (10473, 'Patiala'), (10474, 'Rupnagar'), (10475, 'Sangrur'), (10476, 'SAS Nagar (Mohali)'), (10477, 'Tarn Taran'), (10478, 'Ajmer'), (10479, 'Alwar'), (10480, 'Banswara'), (10481, 'Baran'), (10482, 'Barmer'), (10483, 'Bharatpur'), (10484, 'Bhilwara'), (10485, 'Bikaner'), (10486, 'Bundi'), (10487, 'Chittorgarh'), (10488, 'Churu'), (10489, 'Dausa'), (10490, 'Dholpur'), (10491, 'Dungarpur'), (10492, 'Hanumangarh'), (10493, 'Jaipur'), (10494, 'Jaisalmer'), (10495, 'Jalore'), (10496, 'Jhalawar'), (10497, 'Jhunjhunu'), (10498, 'Jodhpur'), (10499, 'Karauli'), (10500, 'Kota'), (10501, 'Nagaur'), (10502, 'Pali'), (10503, 'Pratapgarh'), (10504, 'Rajsamand'), (10505, 'Sawai Madhopur'), (10506, 'Sikar'), (10507, 'Sirohi'), (10508, 'Sri Ganganagar'), (10509, 'Tonk'), (10510, 'Udaipur'), (10511, 'East Sikkim'), (10512, 'North Sikkim'), (10513, 'South Sikkim'), (10514, 'West Sikkim'), (10515, 'Ariyalur'), (10516, 'Chennai'), (10517, 'Coimbatore'), (10518, 'Cuddalore'), (10519, 'Dharmapuri'), (10520, 'Dindigul'), (10521, 'Erode'), (10522, 'Kanchipuram'), (10523, 'Kanyakumari'), (10524, 'Karur'), (10525, 'Krishnagiri'), (10526, 'Madurai'), (10527, 'Nagapattinam'), (10528, 'Namakkal'), (10529, 'Nilgiris'), (10530, 'Perambalur'), (10531, 'Pudukkottai'), (10532, 'Ramanathapuram'), (10533, 'Salem'), (10534, 'Sivaganga'), (10535, 'Thanjavur'), (10536, 'Theni'), (10537, 'Thoothukudi (Tuticorin)'), (10538, 'Tiruchirappalli'), (10539, 'Tirunelveli'), (10540, 'Tiruppur'), (10541, 'Tiruvallur'), (10542, 'Tiruvannamalai'), (10543, 'Tiruvarur'), (10544, 'Vellore'), (10545, 'Viluppuram'), (10546, 'Virudhunagar'), (10547, 'Adilabad'), (10548, 'Hyderabad'), (10549, 'Karimnagar'), (10550, 'Khammam'), (10551, 'Mahabubnagar'), (10552, 'Medak'), (10553, 'Nalgonda'), (10554, 'Nizamabad'), (10555, 'Rangareddy'), (10556, 'Warangal'), (10557, 'Dhalai'), (10558, 'Gomati'), (10559, 'Khowai'), (10560, 'North Tripura'), (10561, 'Sepahijala'), (10562, 'South Tripura'), (10563, 'Unakoti'), (10564, 'West Tripura'), (10565, 'Agra'), (10566, 'Aligarh'), (10567, 'Allahabad'), (10568, 'Ambedkar Nagar'), (10569, 'Auraiya'), (10570, 'Azamgarh'), (10571, 'Baghpat'), (10572, 'Bahraich'), (10573, 'Ballia'), (10574, 'Balrampur'), (10575, 'Banda'), (10576, 'Barabanki'), (10577, 'Bareilly'), (10578, 'Basti'), (10579, 'Bhim Nagar'), (10580, 'Bijnor'), (10581, 'Budaun'), (10582, 'Bulandshahr'), (10583, 'Chandauli'), (10584, 'Chatrapati Sahuji Mahraj Nagar'), (10585, 'Chitrakoot'), (10586, 'Deoria'), (10587, 'Etah'), (10588, 'Etawah'), (10589, 'Faizabad'), (10590, 'Farrukhabad'), (10591, 'Fatehpur'), (10592, 'Firozabad'), (10593, 'Gautam Buddha Nagar'), (10594, 'Ghaziabad'), (10595, 'Ghazipur'), (10596, 'Gonda'), (10597, 'Gorakhpur'), (10598, 'Hamirpur'), (10599, 'Hardoi'), (10600, 'Hathras'), (10601, 'Jalaun'), (10602, 'Jaunpur'), (10603, 'Jhansi'), (10604, 'Jyotiba Phule Nagar (J.P. Nagar)'), (10605, 'Kannauj'), (10606, 'Kanpur Dehat'), (10607, 'Kanpur Nagar'), (10608, 'Kanshiram Nagar (Kasganj)'), (10609, 'Kaushambi'), (10610, 'Kushinagar (Padrauna)'), (10611, 'Lakhimpur - Kheri'), (10612, 'Lalitpur'), (10613, 'Lucknow'), (10614, 'Maharajganj'), (10615, 'Mahoba'), (10616, 'Mainpuri'), (10617, 'Mathura'), (10618, 'Mau'), (10619, 'Meerut'), (10620, 'Mirzapur'), (10621, 'Moradabad'), (10622, 'Muzaffarnagar'), (10623, 'Panchsheel Nagar'), (10624, 'Pilibhit'), (10625, 'Prabuddh Nagar'), (10626, 'Pratapgarh'), (10627, 'RaeBareli'), (10628, 'Rampur'), (10629, 'Saharanpur'), (10630, 'Sant Kabir Nagar'), (10631, 'Sant Ravidas Nagar'), (10632, 'Shahjahanpur'), (10633, 'Shravasti'), (10634, 'Siddharth Nagar'), (10635, 'Sitapur'), (10636, 'Sonbhadra'), (10637, 'Sultanpur'), (10638, 'Unnao'), (10639, 'Varanasi'), (10640, 'Almora'), (10641, 'Bageshwar'), (10642, 'Chamoli'), (10643, 'Champawat'), (10644, 'Dehradun'), (10645, 'Haridwar'), (10646, 'Nainital'), (10647, 'Pauri Garhwal'), (10648, 'Pithoragarh'), (10649, 'Rudraprayag'), (10650, 'Tehri Garhwal'), (10651, 'Udham Singh Nagar'), (10652, 'Uttarkashi'), (10653, 'Bankura'), (10654, 'Birbhum'), (10655, 'Burdwan (Bardhaman)'), (10656, 'Cooch Behar'), (10657, 'Dakshin Dinajpur (South Dinajpur)'), (10658, 'Darjeeling'), (10659, 'Hooghly'), (10660, 'Howrah'), (10661, 'Jalpaiguri'), (10662, 'Kolkata'), (10663, 'Malda'), (10664, 'Murshidabad'), (10665, 'Nadia'), (10666, 'North 24 Parganas'), (10667, 'Paschim Medinipur (West Medinipur)'), (10668, 'Purba Medinipur (East Medinipur)'), (10669, 'Purulia'), (10670, 'South 24 Parganas'), (10671, 'Noida'), (10671, 'Uttar Dinajpur (North Dinajpur)')], null=True)),
                ('city_text', models.CharField(blank=True, max_length=30)),
                ('date_of_birth', models.DateTimeField(blank=True, null=True)),
                ('display_picture', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_display_picture_path)),
                ('cover_picture', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_cover_picture_path)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('registration_source', models.IntegerField(choices=[(1, 'normal'), (2, 'facebook'), (3, 'google'), (4, 'twitter')], default=1)),
                ('registration_midout', models.BooleanField(default=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=70, unique=True)),
                ('social_profile_id', models.CharField(blank=True, max_length=40, null=True, unique=True)),
                ('tour_completed', models.BooleanField(default=True)),
                ('last_profile_complation_mail', models.DateTimeField(auto_now_add=True)),
                ('friends', models.ManyToManyField(blank=True, related_name='_user_friends_+', to='accounts.User')),
            ],
            options={
                'ordering': ['first_name'],
                'verbose_name': 'user',
            },
        ),
        migrations.AddField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_received', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_sent', to=settings.AUTH_USER_MODEL),
        ),
    ]
