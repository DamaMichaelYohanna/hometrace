import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, AgentProfile, BuyerProfile
from properties.models import Property, PropertyCategory, Amenity, PropertyImage
from messaging.models import Conversation, Message, Enquiry
from favorites.models import Favorite
from payments.models import Payment
from notifications.models import Notification

# Authentic local real estate photographs in Keffi, Nasarawa State
KEFFI_USER_PHOTOS = {
    'bungalow_compound': '/static/images/keffi/keffi_bungalow_compound.webp',
    'modern_bungalow': '/static/images/keffi/keffi_modern_bungalow.webp',
    'student_hostel': '/static/images/keffi/keffi_student_hostel.jpg',
    'duplex_interior': '/static/images/keffi/keffi_duplex_interior.jpg',
    'living_room': '/static/images/keffi/keffi_living_room.webp',
    'kitchen': '/static/images/keffi/keffi_kitchen.jpg',
}

# Curated supplementary photography for Keffi properties
PHOTOS_RESIDENTIAL = [
    KEFFI_USER_PHOTOS['modern_bungalow'],
    KEFFI_USER_PHOTOS['living_room'],
    KEFFI_USER_PHOTOS['kitchen'],
]

PHOTOS_FLATS = [
    KEFFI_USER_PHOTOS['bungalow_compound'],
    KEFFI_USER_PHOTOS['living_room'],
    KEFFI_USER_PHOTOS['kitchen'],
]

PHOTOS_HOSTELS = [
    KEFFI_USER_PHOTOS['student_hostel'],
    KEFFI_USER_PHOTOS['bungalow_compound'],
    KEFFI_USER_PHOTOS['kitchen'],
]

PHOTOS_DUPLEX = [
    KEFFI_USER_PHOTOS['duplex_interior'],
    KEFFI_USER_PHOTOS['living_room'],
    KEFFI_USER_PHOTOS['kitchen'],
]

PHOTOS_COMMERCIAL = [
    "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1000&q=80",
    KEFFI_USER_PHOTOS['duplex_interior'],
]

PHOTOS_LAND = [
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1000&q=80",
]


class Command(BaseCommand):
    help = 'Populates the database with realistic Keffi, Nasarawa State real estate data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing Hometrace Real Estate data for Keffi, Nasarawa State..."))

        # Clean existing demo properties to ensure pure Keffi data
        Property.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared previous property listings."))

        # 1. Categories
        categories_data = [
            ("Apartments & Flats", "building", "Modern 1, 2, and 3-bedroom apartments with steady water and prepaid meters across Keffi."),
            ("Student Hostels & Self-Contains", "home", "Verified student hostels and self-contain rooms near NSUK Main Campus and Angwan Lambu."),
            ("Residential Houses & Duplexes", "home", "Executive detached bungalows, duplexes and family compound residences in GRA Keffi."),
            ("Land & Plots", "map", "Surveyed residential and commercial building plots with verified R of O and C of O in Keffi."),
            ("Commercial & Shops", "briefcase", "Commercial retail shops, office suites, and business plazas along FMC Road and Abuja-Keffi road."),
        ]
        created_categories = {}
        for name, icon, desc in categories_data:
            cat, _ = PropertyCategory.objects.get_or_create(
                name=name,
                defaults={'icon_name': icon, 'description': desc, 'is_active': True}
            )
            created_categories[name] = cat
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_categories)} categories."))

        # 2. Amenities
        amenities_data = [
            ("PHCN Electricity", "utility"),
            ("Private Prepaid Meter", "utility"),
            ("Standby Heavy-Duty Generator", "utility"),
            ("Solar Inverter System", "utility"),
            ("Dedicated Borehole & Overhead Tank", "utility"),
            ("Fenced Compound with Gate", "security"),
            ("24/7 Uniformed Security", "security"),
            ("Ample Car Parking", "comfort"),
            ("Tiled Floors & POP Ceiling", "comfort"),
            ("Private Balcony", "comfort"),
            ("Fitted Kitchen & Cabinets", "comfort"),
            ("Close to NSUK Main Campus", "comfort"),
            ("Walking Distance to FMC", "comfort"),
            ("Proximity to Abuja Expressway", "comfort"),
        ]
        created_amenities = []
        for name, category in amenities_data:
            am, _ = Amenity.objects.get_or_create(name=name, defaults={'category': category})
            created_amenities.append(am)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_amenities)} amenities."))

        # 3. Administrator
        admin_user, _ = User.objects.get_or_create(
            email='admin@hometrace.ng',
            defaults={
                'full_name': 'Hometrace Keffi Administrator',
                'phone_number': '+2348001112233',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
                'is_active': True,
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("Configured Administrator."))

        # 4. Property Agents in Keffi, Nasarawa State
        agents_data = [
            {
                'email': 'agent1@hometrace.ng',
                'name': 'Alhaji Danladi Usman',
                'phone': '+2348035550101',
                'agency': 'Keffi Heritage Properties & Realty',
                'license': 'REDAN/NS/2021/045',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'address': 'Suite 12, Emir Palace Road, Central Keffi, Nasarawa State',
                'whatsapp': '+2348035550101',
                'verified': True,
                'bio': 'Over 14 years serving property buyers, civil servants, and university community members across Keffi with verified titles and genuine documentation.'
            },
            {
                'email': 'agent2@hometrace.ng',
                'name': 'Hajiya Fatima Al-Hassan',
                'phone': '+2348025550202',
                'agency': 'NSUK Campus & Prime Estates Keffi',
                'license': 'REDAN/NS/2022/112',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'address': 'Near NSUK Main Gate, Angwan Lambu, Keffi, Nasarawa State',
                'whatsapp': '+2348025550202',
                'verified': True,
                'bio': 'Specialist in student hostels, self-contains, executive residential apartments, and commercial plazas around Angwan Lambu, Pyanku, and GRA Keffi.'
            },
            {
                'email': 'agent3@hometrace.ng',
                'name': 'Barrister Ibrahim Tanko',
                'phone': '+2348095550303',
                'agency': 'Nasarawa Title Consult & Properties',
                'license': 'REDAN/NS/2020/078',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'address': 'High Court Road, Adjacent FMC, GRA Keffi, Nasarawa State',
                'whatsapp': '+2348095550303',
                'verified': True,
                'bio': 'Legal practitioner and certified property broker guaranteeing title perfection, survey plan verification, and secure transactions in Keffi.'
            },
        ]
        created_agents = []
        for ag_info in agents_data:
            ag_user, _ = User.objects.get_or_create(
                email=ag_info['email'],
                defaults={
                    'full_name': ag_info['name'],
                    'phone_number': ag_info['phone'],
                    'role': User.Role.AGENT,
                    'is_verified': True,
                    'is_active': True,
                }
            )
            ag_user.set_password('AgentPass123!')
            ag_user.save()

            AgentProfile.objects.update_or_create(
                user=ag_user,
                defaults={
                    'agency_name': ag_info['agency'],
                    'license_number': ag_info['license'],
                    'state': ag_info['state'],
                    'city': ag_info['city'],
                    'office_address': ag_info['address'],
                    'whatsapp_number': ag_info['whatsapp'],
                    'is_verified_agent': ag_info['verified'],
                    'biography': ag_info['bio']
                }
            )
            created_agents.append(ag_user)
        self.stdout.write(self.style.SUCCESS("Configured 3 Keffi-based Accredited Agents."))

        # 5. 10 Buyers / Renters in Keffi
        buyers_data = [
            ('buyer1@hometrace.ng', 'Tariq Mohammed (NSUK Student)', '+2348055550001', 'Nasarawa', 'Keffi', Decimal('350000.00')),
            ('buyer2@hometrace.ng', 'Dr. Ngozi Eze (FMC Staff)', '+2348055550002', 'Nasarawa', 'Keffi', Decimal('1200000.00')),
            ('buyer3@hometrace.ng', 'Femi Adeyemi (Abuja Commuter)', '+2348055550003', 'Nasarawa', 'Keffi', Decimal('25000000.00')),
            ('buyer4@hometrace.ng', 'Zainab Bello (Undergraduate)', '+2348055550004', 'Nasarawa', 'Keffi', Decimal('220000.00')),
            ('buyer5@hometrace.ng', 'Chidi Nwosu (Investor)', '+2348055550005', 'Nasarawa', 'Keffi', Decimal('45000000.00')),
            ('buyer6@hometrace.ng', 'Folake Olatunji (NSUK Lecturer)', '+2348055550006', 'Nasarawa', 'Keffi', Decimal('850000.00')),
            ('buyer7@hometrace.ng', 'Ibrahim Garba (Contractor)', '+2348055550007', 'Nasarawa', 'Keffi', Decimal('30000000.00')),
            ('buyer8@hometrace.ng', 'Blessing Jumbo (Nurse)', '+2348055550008', 'Nasarawa', 'Keffi', Decimal('700000.00')),
            ('buyer9@hometrace.ng', 'Kelechi Madu (Store Owner)', '+2348055550009', 'Nasarawa', 'Keffi', Decimal('1500000.00')),
            ('buyer10@hometrace.ng', 'Ayomide Cole (Civil Servant)', '+2348055550010', 'Nasarawa', 'Keffi', Decimal('15000000.00')),
        ]
        created_buyers = []
        for email, name, phone, state, city, budget in buyers_data:
            b_user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': name,
                    'phone_number': phone,
                    'role': User.Role.BUYER,
                    'is_verified': True,
                    'is_active': True,
                }
            )
            b_user.set_password('BuyerPass123!')
            b_user.save()

            BuyerProfile.objects.update_or_create(
                user=b_user,
                defaults={
                    'preferred_state': state,
                    'preferred_city': city,
                    'max_budget': budget,
                }
            )
            created_buyers.append(b_user)
        self.stdout.write(self.style.SUCCESS("Configured 10 Buyer accounts."))

        # 6. Realistic Keffi, Nasarawa State Property Listings (24 listings across Keffi)
        properties_catalog = [
            # 1. GRA Keffi Executive Bungalow
            {
                'title': 'Contemporary 4-Bedroom Detached Bungalow with BQ, GRA Keffi',
                'category': 'Residential Houses & Duplexes',
                'purpose': 'for_sale',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'GRA Keffi',
                'address': 'Plot 18, VIP Road, GRA',
                'price': Decimal('55000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 4, 'baths': 4, 'toilets': 5, 'parking': 4, 'size': 500.0,
                'furnished': 'semi_furnished', 'condition': 'brand_new', 'featured': True,
                'agent_index': 0,
                'photos': PHOTOS_RESIDENTIAL,
                'description': 'Elegantly built 4-bedroom detached bungalow located in the serene and secure Government Reserved Area (GRA) of Keffi. Built on a standard 500sqm plot with interlocked compound, borehole, electric fence, and 1-room BQ. Title: Right of Occupancy (R of O).'
            },
            # 2. Angwan Lambu Student Hostel
            {
                'title': 'Newly Built 12-Room Executive Student Hostel near NSUK Main Gate',
                'category': 'Student Hostels & Self-Contains',
                'purpose': 'for_sale',
                'type': 'commercial',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Angwan Lambu',
                'address': 'University Road, Angwan Lambu',
                'price': Decimal('42000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 12, 'baths': 12, 'toilets': 12, 'parking': 3, 'size': 650.0,
                'furnished': 'semi_furnished', 'condition': 'brand_new', 'featured': True,
                'agent_index': 1,
                'photos': PHOTOS_HOSTELS,
                'description': 'High-yield investment property situated just 4 minutes walk from the Nasarawa State University Keffi (NSUK) main gate. 12 self-contained studio units each fitted with personal kitchenettes, prepaid sub-meters, and continuous borehole water supply.'
            },
            # 3. GRA Keffi Executive Duplex
            {
                'title': 'Luxury 5-Bedroom Detached Duplex with Security Post, GRA Keffi',
                'category': 'Residential Houses & Duplexes',
                'purpose': 'for_sale',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'GRA Keffi',
                'address': 'Court Road, GRA Phase 2',
                'price': Decimal('75000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 5, 'baths': 5, 'toilets': 6, 'parking': 5, 'size': 600.0,
                'furnished': 'semi_furnished', 'condition': 'brand_new', 'featured': True,
                'agent_index': 2,
                'photos': PHOTOS_DUPLEX,
                'description': 'Ultra-modern 5-bedroom duplex with exquisite contemporary finishing in the most sought-after quarter of GRA Keffi. Features spacious living rooms, POP ceiling, granite flooring, dedicated solar inverter connection, and security post.'
            },
            # 4. FMC Road Modern 2-Bedroom Flat
            {
                'title': 'Serviced 2-Bedroom Flat in Gated Compound, FMC Keffi Road',
                'category': 'Apartments & Flats',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'FMC Corridor',
                'address': 'Near Federal Medical Centre, Keffi',
                'price': Decimal('750000.00'),
                'freq': 'yearly',
                'negotiable': False,
                'beds': 2, 'baths': 2, 'toilets': 3, 'parking': 2, 'size': 110.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': True,
                'agent_index': 2,
                'photos': PHOTOS_FLATS,
                'description': 'Spacious and well-aerated 2-bedroom flat located along the Federal Medical Centre road. Proximity to FMC makes it ideal for medical personnel, civil servants, and families. Borehole water and private prepaid meter included.'
            },
            # 5. Angwan Lambu Self-Contain Studio
            {
                'title': 'Modern Self-Contain Apartment with POP Ceiling, Angwan Lambu',
                'category': 'Student Hostels & Self-Contains',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Angwan Lambu',
                'address': 'Behind Total Station, Angwan Lambu',
                'price': Decimal('220000.00'),
                'freq': 'yearly',
                'negotiable': False,
                'beds': 1, 'baths': 1, 'toilets': 1, 'parking': 1, 'size': 40.0,
                'furnished': 'semi_furnished', 'condition': 'brand_new', 'featured': True,
                'agent_index': 1,
                'photos': PHOTOS_HOSTELS,
                'description': 'Clean, fully-tiled student self-contain room in a secure fenced compound with security gate. Features running borehole water, wardrobe, private bath and toilet, and personal prepaid meter. 5 minutes from NSUK campus.'
            },
            # 6. Commercial Shops on Abuja-Keffi Expressway
            {
                'title': 'Prime Commercial Complex with 6 Lock-up Shops, Abuja-Keffi Road',
                'category': 'Commercial & Shops',
                'purpose': 'for_rent',
                'type': 'commercial',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Abuja-Keffi Expressway',
                'address': 'Opposite Total Filling Station, Expressway',
                'price': Decimal('1500000.00'),
                'freq': 'yearly',
                'negotiable': True,
                'beds': 0, 'baths': 2, 'toilets': 2, 'parking': 6, 'size': 240.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': True,
                'agent_index': 0,
                'photos': PHOTOS_COMMERCIAL,
                'description': 'High-visibility roadside commercial plaza on the bustling Abuja-Keffi expressway corridor. Excellent footfall and highway exposure suitable for pharmacy, retail supermarket, logistics hub, or corporate branches.'
            },
            # 7. High Court Road 3-Bedroom Flat
            {
                'title': 'Standard 3-Bedroom Flat with Constant Water, High Court Road',
                'category': 'Apartments & Flats',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'High Court Road',
                'address': 'Adjacent High Court Complex, Keffi',
                'price': Decimal('950000.00'),
                'freq': 'yearly',
                'negotiable': True,
                'beds': 3, 'baths': 2, 'toilets': 3, 'parking': 2, 'size': 150.0,
                'furnished': 'unfurnished', 'condition': 'renovated', 'featured': False,
                'agent_index': 2,
                'photos': PHOTOS_FLATS,
                'description': 'Family-friendly 3-bedroom flat in a quiet and secure residential zone off High Court Road. Compound has interlocked floor, perimeter fence, constant borehole water, and dedicated parking.'
            },
            # 8. Commercial Land along Expressway
            {
                'title': '2 Plots of Prime Commercial Land on Abuja-Keffi Expressway',
                'category': 'Land & Plots',
                'purpose': 'for_sale',
                'type': 'land',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Abuja-Keffi Expressway',
                'address': 'Beside Conoil Station, Expressway Corridor',
                'price': Decimal('18000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 0, 'baths': 0, 'toilets': 0, 'parking': 0, 'size': 1200.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 0,
                'photos': PHOTOS_LAND,
                'description': 'Fenced commercial parcel measuring 1,200 square meters fronting the active expressway. Ideal for gas plant, transport terminal, hotel, or retail shopping mall. Verified Right of Occupancy with survey plan.'
            },
            # 9. Tudun Kofa 3-Bedroom Bungalow
            {
                'title': 'Newly Completed 3-Bedroom Bungalow on Full Plot, Tudun Kofa',
                'category': 'Residential Houses & Duplexes',
                'purpose': 'for_sale',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Tudun Kofa',
                'address': 'Behind Central Mosque Road, Tudun Kofa',
                'price': Decimal('28000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 3, 'baths': 3, 'toilets': 4, 'parking': 3, 'size': 450.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 0,
                'photos': PHOTOS_DUPLEX,
                'description': 'Decent and solidly constructed 3-bedroom bungalow with all rooms ensuite. Features good road network access, functional borehole, spacious compound with room for further development, and perimeter fencing.'
            },
            # 10. Pyanku Student Self-Contain
            {
                'title': 'Clean Self-Contain Room with Prepaid Meter, Pyanku Extension',
                'category': 'Student Hostels & Self-Contains',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Pyanku',
                'address': 'Pyanku Layout, off Keffi-Akwanga Road',
                'price': Decimal('180000.00'),
                'freq': 'yearly',
                'negotiable': False,
                'beds': 1, 'baths': 1, 'toilets': 1, 'parking': 1, 'size': 35.0,
                'furnished': 'semi_furnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 1,
                'photos': PHOTOS_HOSTELS,
                'description': 'Affordable student single-room self-contain in rapidly developing Pyanku neighborhood. Secure gate, steady water supply, clean tiles, and reliable neighbourhood security.'
            },
            # 11. Yalwa Residential Plot
            {
                'title': 'Dry Residential Land Measuring 600sqm with Beacon Stones, Yalwa',
                'category': 'Land & Plots',
                'purpose': 'for_sale',
                'type': 'land',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Yalwa',
                'address': 'Yalwa Residential Layout, Keffi',
                'price': Decimal('5500000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 0, 'baths': 0, 'toilets': 0, 'parking': 0, 'size': 600.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 2,
                'photos': PHOTOS_LAND,
                'description': 'Ready-to-build dry residential land in an established residential community. Surrounded by inhabited homes, electricity grid connection nearby, and verified local government allocation papers.'
            },
            # 12. Angwan Lambu Block of Flats
            {
                'title': 'Block of 4 Units of 2-Bedroom Flats for Investment, Angwan Lambu',
                'category': 'Apartments & Flats',
                'purpose': 'for_sale',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Angwan Lambu',
                'address': 'Main Campus Road, Angwan Lambu',
                'price': Decimal('38000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 8, 'baths': 8, 'toilets': 12, 'parking': 4, 'size': 500.0,
                'furnished': 'unfurnished', 'condition': 'renovated', 'featured': False,
                'agent_index': 1,
                'photos': PHOTOS_FLATS,
                'description': 'Fully tenanted property generating steady annual rental returns from university staff and postgraduates. Features 4 units of 2-bedroom flats, constant borehole water, and prepaid meters for each apartment.'
            },
            # 13. GRA Keffi 3-Bedroom Detached Bungalow
            {
                'title': 'Spacious 3-Bedroom Bungalow with Green Garden, GRA Keffi',
                'category': 'Residential Houses & Duplexes',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'GRA Keffi',
                'address': 'Judiciary Close, GRA',
                'price': Decimal('1800000.00'),
                'freq': 'yearly',
                'negotiable': True,
                'beds': 3, 'baths': 3, 'toilets': 4, 'parking': 3, 'size': 350.0,
                'furnished': 'semi_furnished', 'condition': 'renovated', 'featured': False,
                'agent_index': 0,
                'photos': PHOTOS_DUPLEX,
                'description': 'Spacious executive home with serene garden surroundings. Very quiet neighborhood with top-tier security, paved driveway, constant solar water heating, and standby generator connection.'
            },
            # 14. FMC Hospital Road 1-Bedroom Mini Flat
            {
                'title': 'Decent 1-Bedroom Mini Flat with Private Prepaid Meter, FMC Road',
                'category': 'Apartments & Flats',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'FMC Corridor',
                'address': 'Hospital By-pass, near FMC Gate 2',
                'price': Decimal('400000.00'),
                'freq': 'yearly',
                'negotiable': False,
                'beds': 1, 'baths': 1, 'toilets': 1, 'parking': 1, 'size': 55.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 2,
                'photos': PHOTOS_FLATS,
                'description': 'Newly painted 1-bedroom flat comprising sitting room, bedroom, kitchen, and bathroom. Well-fenced compound with running borehole water and 24-hour gate security. 3 minutes from FMC Keffi.'
            },
            # 15. Sabon Gari Commercial Store
            {
                'title': 'Commercial Storefront & Warehouse Space, Sabon Gari Keffi',
                'category': 'Commercial & Shops',
                'purpose': 'for_rent',
                'type': 'commercial',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Sabon Gari',
                'address': 'Market Road, Sabon Gari',
                'price': Decimal('850000.00'),
                'freq': 'yearly',
                'negotiable': True,
                'beds': 0, 'baths': 1, 'toilets': 1, 'parking': 2, 'size': 80.0,
                'furnished': 'unfurnished', 'condition': 'renovated', 'featured': False,
                'agent_index': 0,
                'photos': PHOTOS_COMMERCIAL,
                'description': 'Commercial shop space situated in the active commercial heart of Keffi. Excellent road accessibility for goods delivery, iron burglary protection, and prepaid power meter.'
            },
            # 16. Pyanku Residential Plot
            {
                'title': 'Residential Plot of Land (500sqm) in University Extension, Pyanku',
                'category': 'Land & Plots',
                'purpose': 'for_sale',
                'type': 'land',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Pyanku',
                'address': 'Off Akwanga Road, Pyanku',
                'price': Decimal('4200000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 0, 'baths': 0, 'toilets': 0, 'parking': 0, 'size': 500.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 1,
                'photos': PHOTOS_LAND,
                'description': 'Affordable 500sqm parcel suited for developing private student hostels or family residence. Level terrain, zero flooding risk, and accessible access road.'
            },
            # 17. Main Campus NSUK Executive Hostel Room
            {
                'title': 'Executive Student Self-Contain with Kitchenette, NSUK Main Campus',
                'category': 'Student Hostels & Self-Contains',
                'purpose': 'for_rent',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'Main Campus NSUK',
                'address': 'Faculty Road, Campus Perimeter',
                'price': Decimal('250000.00'),
                'freq': 'yearly',
                'negotiable': False,
                'beds': 1, 'baths': 1, 'toilets': 1, 'parking': 1, 'size': 45.0,
                'furnished': 'semi_furnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 1,
                'photos': PHOTOS_HOSTELS,
                'description': 'Premium student room designed for serious academics and postgraduate students. Fully tiled, fitted wardrobe, personal balcony, treated water system, and security personnel.'
            },
            # 18. High Court Road 4-Bedroom Semi-Detached
            {
                'title': 'Modern 4-Bedroom Semi-Detached Duplex, High Court Road',
                'category': 'Residential Houses & Duplexes',
                'purpose': 'for_sale',
                'type': 'residential',
                'state': 'Nasarawa',
                'city': 'Keffi',
                'lga': 'Keffi',
                'neighbourhood': 'High Court Road',
                'address': 'Near Ministry Quarters, High Court Road',
                'price': Decimal('48000000.00'),
                'freq': None,
                'negotiable': True,
                'beds': 4, 'baths': 4, 'toilets': 5, 'parking': 3, 'size': 400.0,
                'furnished': 'unfurnished', 'condition': 'brand_new', 'featured': False,
                'agent_index': 2,
                'photos': PHOTOS_DUPLEX,
                'description': 'Contemporary 4-bedroom semi-detached residence built with top-quality materials. Features pop design, spacious family lounge, paved driveway, and clean legal title documentation.'
            },
        ]

        created_properties = []
        for index, item in enumerate(properties_catalog):
            agent = created_agents[item['agent_index']]
            category = created_categories[item['category']]

            prop, created = Property.objects.get_or_create(
                title=item['title'],
                defaults={
                    'agent': agent,
                    'category': category,
                    'listing_purpose': item['purpose'],
                    'property_type': item['type'],
                    'state': item['state'],
                    'city': item['city'],
                    'lga': item['lga'],
                    'neighbourhood': item['neighbourhood'],
                    'street_address': item['address'],
                    'price': item['price'],
                    'rental_frequency': item['freq'],
                    'is_negotiable': item['negotiable'],
                    'bedrooms': item['beds'],
                    'bathrooms': item['baths'],
                    'toilets': item['toilets'],
                    'parking_spaces': item['parking'],
                    'property_size': item['size'],
                    'furnished_status': item['furnished'],
                    'property_condition': item['condition'],
                    'is_featured': item['featured'],
                    'approval_status': Property.ApprovalStatus.APPROVED,
                    'availability_status': Property.AvailabilityStatus.AVAILABLE,
                    'description': item['description'],
                    'view_count': random.randint(30, 480),
                    'published_at': timezone.now() - timezone.timedelta(days=random.randint(1, 20)),
                }
            )

            # Assign 5-8 amenities
            prop.amenities.set(random.sample(created_amenities, random.randint(5, 8)))

            # Create images for each property with curated photo list
            if prop.images.count() == 0:
                photos_to_use = item.get('photos', PHOTOS_RESIDENTIAL)
                for order, photo_url in enumerate(photos_to_use):
                    PropertyImage.objects.create(
                        property=prop,
                        image=photo_url,
                        caption=f"View of {item['neighbourhood']} property ({order + 1})",
                        is_featured=(order == 0),
                        display_order=order
                    )

            created_properties.append(prop)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_properties)} authentic Keffi, Nasarawa State listings."))

        # 7. Sample Enquiries & Conversations
        sample_buyer = created_buyers[0]
        sample_agent = created_agents[0]
        sample_property = created_properties[0]

        conv, _ = Conversation.objects.get_or_create(
            buyer=sample_buyer,
            agent=sample_agent,
            property=sample_property
        )

        if conv.messages.count() == 0:
            Message.objects.create(
                conversation=conv,
                sender=sample_buyer,
                body=f"Hello Alhaji Danladi, my name is {sample_buyer.full_name}. Is this {sample_property.neighbourhood} property still available for physical inspection this Saturday?"
            )
            Message.objects.create(
                conversation=conv,
                sender=sample_agent,
                body=f"Hello Mr. Mohammed, yes it is available. The compound is fully fenced with borehole water. We can arrange inspection by 11:00 AM."
            )
            Message.objects.create(
                conversation=conv,
                sender=sample_buyer,
                body="Thank you sir! I have scheduled the inspection deposit through Hometrace. See you in Keffi on Saturday."
            )

        Enquiry.objects.get_or_create(
            buyer=sample_buyer,
            agent=sample_agent,
            property=sample_property,
            defaults={
                'subject': f"Inspection Inquiry: {sample_property.title[:40]}",
                'message': "Seeking physical inspection confirmation and copy of survey plan in Keffi.",
                'status': 'responded'
            }
        )

        # 8. Sample Favorites
        for buyer in created_buyers[:5]:
            for prop in random.sample(created_properties, 3):
                Favorite.objects.get_or_create(user=buyer, property=prop)

        # 9. Sample Paystack Payment Records
        payments_sample = [
            (created_agents[0], 'HT-20261101-A48EF1', Decimal('15000.00'), Payment.Purpose.AGENT_VERIFICATION, Payment.Status.SUCCESS),
            (created_agents[1], 'HT-20261102-B92CD2', Decimal('15000.00'), Payment.Purpose.AGENT_VERIFICATION, Payment.Status.SUCCESS),
            (created_agents[2], 'HT-20261103-C34DA3', Decimal('15000.00'), Payment.Purpose.AGENT_VERIFICATION, Payment.Status.SUCCESS),
            (created_buyers[0], 'HT-20261104-D18FE4', Decimal('5000.00'), Payment.Purpose.INSPECTION_FEE, Payment.Status.SUCCESS),
            (created_buyers[1], 'HT-20261105-E99AA5', Decimal('5000.00'), Payment.Purpose.INSPECTION_FEE, Payment.Status.SUCCESS),
            (created_agents[0], 'HT-20261106-F88BB6', Decimal('10000.00'), Payment.Purpose.LISTING_FEATURE, Payment.Status.SUCCESS),
        ]

        for u, ref, amt, purp, st in payments_sample:
            Payment.objects.get_or_create(
                reference=ref,
                defaults={
                    'user': u,
                    'amount': amt,
                    'purpose': purp,
                    'status': st,
                    'channel': 'card',
                    'property': sample_property if purp in (Payment.Purpose.INSPECTION_FEE, Payment.Purpose.LISTING_FEATURE) else None,
                    'paid_at': timezone.now() - timezone.timedelta(days=random.randint(1, 10))
                }
            )

        # 10. Notifications
        for buyer in created_buyers[:4]:
            Notification.objects.get_or_create(
                user=buyer,
                title="Welcome to Hometrace Keffi",
                defaults={
                    'message': "Discover verified student hostels, apartments, and land across Keffi, Nasarawa State.",
                    'notification_type': Notification.NotificationType.SYSTEM,
                    'is_read': False
                }
            )

        self.stdout.write(self.style.SUCCESS("Hometrace Keffi demonstration data loaded successfully!"))
