# Standard Library
import datetime
from decimal import Decimal

# Django
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

# wger
from wger.core.models import (
    Language,
    UserCache,
    UserProfile,
)
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseCategory,
    Muscle,
    Translation,
)
from wger.manager.models import (
    Day,
    Routine,
    Slot,
    SlotEntry,
    WorkoutLog,
)
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.nutrition.models import (
    Ingredient,
    Meal,
    MealItem,
    NutritionPlan,
)


class Command(BaseCommand):
    help = 'Populate rich mock data (users, exercises, ingredients, routines, logs, meal plans, body weights)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting mock data population for HEALTHYFY TRACKER...'))

        # 1. Setup Language
        lang_en, _ = Language.objects.get_or_create(short_name='en')

        # 2. Setup Users
        users_info = [
            {
                'username': 'admin',
                'email': 'admin@healthyfy.com',
                'password': 'admin123',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'Vishaal',
            },
            {
                'username': 'demo',
                'email': 'demo@healthyfy.com',
                'password': 'demo123',
                'is_staff': False,
                'is_superuser': False,
                'first_name': 'Alex',
                'last_name': 'Morgan',
            },
            {
                'username': 'trainer_alex',
                'email': 'trainer@healthyfy.com',
                'password': 'trainer123',
                'is_staff': False,
                'is_superuser': False,
                'first_name': 'Alex',
                'last_name': 'Rivers',
            },
            {
                'username': 'fitness_sarah',
                'email': 'sarah@healthyfy.com',
                'password': 'sarah123',
                'is_staff': False,
                'is_superuser': False,
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
            },
            {
                'username': 'mike_runner',
                'email': 'mike@healthyfy.com',
                'password': 'mike123',
                'is_staff': False,
                'is_superuser': False,
                'first_name': 'Mike',
                'last_name': 'Chen',
            },
        ]

        created_users = {}
        for udata in users_info:
            user, created = User.objects.get_or_create(username=udata['username'])
            user.email = udata['email']
            user.set_password(udata['password'])
            user.first_name = udata['first_name']
            user.last_name = udata['last_name']
            user.is_staff = udata['is_staff']
            user.is_superuser = udata['is_superuser']
            user.is_active = True
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.save()
            UserCache.objects.get_or_create(user=user)

            try:
                Category.get_or_create_body_weight(user, unit=profile.weight_unit)
            except Exception:
                pass

            EmailAddress.objects.filter(user=user).delete()
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=True,
                primary=True,
            )

            created_users[user.username] = user
            self.stdout.write(f'  [User] Ready: {user.username} (Password: {udata["password"]})')

        # Setup Gym & Gym Management
        from django.contrib.auth.models import Permission
        from wger.gym.models import Gym, GymAdminConfig, GymUserConfig

        gym, _ = Gym.objects.get_or_create(
            name='Healthyfy Fitness Center',
            defaults={
                'phone': '+1 (555) 019-2834',
                'email': 'gym@healthyfy.com',
                'owner': 'Vishaal',
                'zip_code': '90210',
                'city': 'Metropolis',
            },
        )

        perm_trainer = Permission.objects.filter(codename='gym_trainer').first()
        perm_manage = Permission.objects.filter(codename='manage_gym').first()
        perm_gyms = Permission.objects.filter(codename='manage_gyms').first()

        for staff_username in ['admin', 'trainer_alex']:
            u = created_users[staff_username]
            for p in [perm_trainer, perm_manage, perm_gyms]:
                if p:
                    u.user_permissions.add(p)
            GymAdminConfig.objects.get_or_create(gym=gym, user=u)

        for member_username in ['demo', 'fitness_sarah', 'mike_runner']:
            u = created_users[member_username]
            GymUserConfig.objects.get_or_create(gym=gym, user=u)

        self.stdout.write('  [Gym] Created Healthyfy Fitness Center with 2 staff & 3 active members')

        # 3. Setup Categories and Equipment
        cat_chest, _ = ExerciseCategory.objects.get_or_create(name='Chest')
        cat_back, _ = ExerciseCategory.objects.get_or_create(name='Back')
        cat_legs, _ = ExerciseCategory.objects.get_or_create(name='Legs')
        cat_shoulders, _ = ExerciseCategory.objects.get_or_create(name='Shoulders')
        cat_arms, _ = ExerciseCategory.objects.get_or_create(name='Arms')
        cat_abs, _ = ExerciseCategory.objects.get_or_create(name='Abs')

        eq_barbell, _ = Equipment.objects.get_or_create(name='Barbell')
        eq_dumbbell, _ = Equipment.objects.get_or_create(name='Dumbbell')
        eq_cable, _ = Equipment.objects.get_or_create(name='Cable machine')
        eq_bodyweight, _ = Equipment.objects.get_or_create(name='none (bodyweight exercise)')
        eq_pullup, _ = Equipment.objects.get_or_create(name='Pull-up bar')

        # 4. Populate Standard Exercises
        exercise_specs = [
            {
                'name': 'Barbell Bench Press',
                'category': cat_chest,
                'equipment': [eq_barbell],
                'desc': 'Lie flat on the bench. Grip the barbell slightly wider than shoulder width. Lower the bar with control to mid-chest, then drive powerfully upward to lockout.',
            },
            {
                'name': 'Incline Dumbbell Press',
                'category': cat_chest,
                'equipment': [eq_dumbbell],
                'desc': 'Set the bench to 30-45 degrees. Press dumbbells overhead with upper chest contraction and full control on the eccentric phase.',
            },
            {
                'name': 'Cable Chest Flyes',
                'category': cat_chest,
                'equipment': [eq_cable],
                'desc': 'Set pulleys to shoulder height. Bring handles together in a hugging motion, squeezing the chest at peak contraction.',
            },
            {
                'name': 'Barbell Back Squat',
                'category': cat_legs,
                'equipment': [eq_barbell],
                'desc': 'Rest the barbell across your upper traps. Break at hips and knees simultaneously, descend to parallel or deeper, and drive back up through midfoot.',
            },
            {
                'name': 'Romanian Deadlift (RDL)',
                'category': cat_legs,
                'equipment': [eq_barbell],
                'desc': 'Hinge at the hips with soft knees, pushing hips back while keeping back flat until you feel a deep hamstring stretch, then return to standing.',
            },
            {
                'name': 'Dumbbell Walking Lunges',
                'category': cat_legs,
                'equipment': [eq_dumbbell],
                'desc': 'Step forward into a lunge until trailing knee gently taps floor. Drive through front heel to step forward into next rep.',
            },
            {
                'name': 'Wide-Grip Pull-Ups',
                'category': cat_back,
                'equipment': [eq_pullup],
                'desc': 'Hang from the bar with palms facing away. Pull your chest toward the bar by driving your elbows down and back.',
            },
            {
                'name': 'Barbell Bent-Over Row',
                'category': cat_back,
                'equipment': [eq_barbell],
                'desc': 'Hinge forward 45 degrees with flat spine. Pull barbell into lower ribcage, squeezing the lats and scapulae together.',
            },
            {
                'name': 'Lat Pulldown',
                'category': cat_back,
                'equipment': [eq_cable],
                'desc': 'Grip the wide bar, lean back slightly, and pull down toward upper chest while driving elbows toward hips.',
            },
            {
                'name': 'Overhead Shoulder Press (OHP)',
                'category': cat_shoulders,
                'equipment': [eq_barbell],
                'desc': 'Stand with bar at collarbones. Press overhead in a straight vertical bar path, locking out with head through the window.',
            },
            {
                'name': 'Dumbbell Lateral Raises',
                'category': cat_shoulders,
                'equipment': [eq_dumbbell],
                'desc': 'Raise dumbbells out to the sides until parallel with floor, focusing entirely on lateral deltoid activation.',
            },
            {
                'name': 'Standing Barbell Bicep Curl',
                'category': cat_arms,
                'equipment': [eq_barbell],
                'desc': 'Curl the barbell toward shoulders with strict form, keeping elbows pinned to your sides for maximal bicep tension.',
            },
            {
                'name': 'Tricep Rope Pushdown',
                'category': cat_arms,
                'equipment': [eq_cable],
                'desc': 'Using rope attachment on high pulley, push downward and spread ropes apart at bottom for peak triceps contraction.',
            },
            {
                'name': 'Hanging Knee Raises',
                'category': cat_abs,
                'equipment': [eq_pullup],
                'desc': 'Hang from bar and raise knees toward chest, contracting abdominals and controlling swing on the descent.',
            },
            {
                'name': 'Plank',
                'category': cat_abs,
                'equipment': [eq_bodyweight],
                'desc': 'Hold rigid pushup position on forearms, keeping core, glutes, and quads tightly braced in a straight line.',
            },
        ]

        exercise_map = {}
        for spec in exercise_specs:
            # Check if translation exists
            trans = Translation.objects.filter(name=spec['name'], language=lang_en).first()
            if trans:
                exercise = trans.exercise
            else:
                exercise = Exercise.objects.create(
                    category=spec['category'],
                    license_id=1,
                )
                exercise.equipment.set(spec['equipment'])
                exercise.save()

                trans = Translation.objects.create(
                    exercise=exercise,
                    name=spec['name'],
                    description=spec['desc'],
                    description_source=spec['desc'],
                    language=lang_en,
                    license_id=1,
                )
            exercise_map[spec['name']] = exercise

        self.stdout.write(f'  [Exercises] Total in DB: {Exercise.objects.count()}')

        # 5. Populate Healthy Nutritional Ingredients
        ingredients_data = [
            {'name': 'Chicken Breast (Grilled)', 'energy': 165, 'protein': Decimal('31.0'), 'carbs': Decimal('0.0'), 'fat': Decimal('3.6')},
            {'name': 'Whole Large Eggs', 'energy': 143, 'protein': Decimal('12.6'), 'carbs': Decimal('0.7'), 'fat': Decimal('9.5')},
            {'name': 'Rolled Whole Oats', 'energy': 389, 'protein': Decimal('16.9'), 'carbs': Decimal('66.3'), 'fat': Decimal('6.9')},
            {'name': 'Greek Yogurt (0% Plain)', 'energy': 59, 'protein': Decimal('10.0'), 'carbs': Decimal('3.6'), 'fat': Decimal('0.4')},
            {'name': 'Whey Protein Isolate', 'energy': 375, 'protein': Decimal('82.0'), 'carbs': Decimal('3.0'), 'fat': Decimal('1.5')},
            {'name': 'Cooked Brown Rice', 'energy': 111, 'protein': Decimal('2.6'), 'carbs': Decimal('23.0'), 'fat': Decimal('0.9')},
            {'name': 'Atlantic Salmon Fillet', 'energy': 208, 'protein': Decimal('20.4'), 'carbs': Decimal('0.0'), 'fat': Decimal('13.0')},
            {'name': 'Baked Sweet Potato', 'energy': 90, 'protein': Decimal('2.0'), 'carbs': Decimal('20.7'), 'fat': Decimal('0.1')},
            {'name': 'Natural Peanut Butter', 'energy': 588, 'protein': Decimal('25.0'), 'carbs': Decimal('20.0'), 'fat': Decimal('50.0')},
            {'name': 'Fresh Banana', 'energy': 89, 'protein': Decimal('1.1'), 'carbs': Decimal('22.8'), 'fat': Decimal('0.3')},
            {'name': 'Extra Virgin Olive Oil', 'energy': 884, 'protein': Decimal('0.0'), 'carbs': Decimal('0.0'), 'fat': Decimal('100.0')},
            {'name': 'Steamed Fresh Broccoli', 'energy': 35, 'protein': Decimal('2.4'), 'carbs': Decimal('7.0'), 'fat': Decimal('0.4')},
            {'name': 'Raw Whole Almonds', 'energy': 579, 'protein': Decimal('21.2'), 'carbs': Decimal('21.6'), 'fat': Decimal('49.9')},
            {'name': 'Low-Fat Cottage Cheese', 'energy': 98, 'protein': Decimal('11.1'), 'carbs': Decimal('3.4'), 'fat': Decimal('4.3')},
            {'name': 'Whole Milk', 'energy': 61, 'protein': Decimal('3.2'), 'carbs': Decimal('4.8'), 'fat': Decimal('3.3')},
        ]

        ing_map = {}
        for idata in ingredients_data:
            ing, _ = Ingredient.objects.get_or_create(
                name=idata['name'],
                defaults={
                    'energy': idata['energy'],
                    'protein': idata['protein'],
                    'carbohydrates': idata['carbs'],
                    'fat': idata['fat'],
                    'language': lang_en,
                    'license_id': 1,
                },
            )
            ing_map[idata['name']] = ing

        self.stdout.write(f'  [Foods / Ingredients] Total in DB: {Ingredient.objects.count()}')

        # 6. Populate Routines & Workouts for demo user
        demo_user = created_users['demo']
        today = datetime.date.today()

        # Demo Routine: Push / Pull / Legs Split
        routine, _ = Routine.objects.get_or_create(
            user=demo_user,
            name='PPL Hypertrophy Split',
            defaults={
                'description': 'Targeted 3-day Push-Pull-Legs split engineered for muscle hypertrophy, strength, and balanced physique development.',
                'start': today - datetime.timedelta(days=30),
                'end': today + datetime.timedelta(days=90),
            },
        )

        # Day 1: Push Day
        day_push, _ = Day.objects.get_or_create(
            routine=routine,
            order=1,
            defaults={'name': 'Push Day (Chest/Delts)', 'description': 'Heavy bench and overhead pressing with shoulder and tricep accessories.'},
        )
        # Day 2: Pull Day
        day_pull, _ = Day.objects.get_or_create(
            routine=routine,
            order=2,
            defaults={'name': 'Pull Day (Back/Biceps)', 'description': 'Vertical and horizontal pulling with direct arm isolation.'},
        )
        # Day 3: Legs Day
        day_legs, _ = Day.objects.get_or_create(
            routine=routine,
            order=3,
            defaults={'name': 'Legs & Core', 'description': 'Squatting, hinge work, and core stabilization.'},
        )

        # Add exercises to Push Day
        if not day_push.slots.exists():
            for i, ex_name in enumerate(['Barbell Bench Press', 'Incline Dumbbell Press', 'Overhead Shoulder Press (OHP)', 'Tricep Rope Pushdown'], start=1):
                slot = Slot.objects.create(day=day_push, order=i)
                SlotEntry.objects.create(slot=slot, exercise=exercise_map[ex_name])

        # Add exercises to Pull Day
        if not day_pull.slots.exists():
            for i, ex_name in enumerate(['Wide-Grip Pull-Ups', 'Barbell Bent-Over Row', 'Lat Pulldown', 'Standing Barbell Bicep Curl'], start=1):
                slot = Slot.objects.create(day=day_pull, order=i)
                SlotEntry.objects.create(slot=slot, exercise=exercise_map[ex_name])

        # Add exercises to Legs Day
        if not day_legs.slots.exists():
            for i, ex_name in enumerate(['Barbell Back Squat', 'Romanian Deadlift (RDL)', 'Dumbbell Walking Lunges', 'Plank'], start=1):
                slot = Slot.objects.create(day=day_legs, order=i)
                SlotEntry.objects.create(slot=slot, exercise=exercise_map[ex_name])

        self.stdout.write('  [Routines] Created Push / Pull / Legs Hypertrophy Split with 12 exercises')

        # 7. Add Logged Workout History (Past 14 Days)
        bench_ex = exercise_map['Barbell Bench Press']
        squat_ex = exercise_map['Barbell Back Squat']

        if not WorkoutLog.objects.filter(user=demo_user).exists():
            for day_offset, weight_val, reps_val in [(12, Decimal('75.0'), Decimal('8')), (9, Decimal('77.5'), Decimal('8')), (5, Decimal('80.0'), Decimal('6')), (1, Decimal('82.5'), Decimal('6'))]:
                log_dt = timezone.now() - datetime.timedelta(days=day_offset, hours=2)
                WorkoutLog.objects.create(
                    user=demo_user,
                    routine=routine,
                    exercise=bench_ex,
                    weight=weight_val,
                    repetitions=reps_val,
                    date=log_dt,
                )

            for day_offset, weight_val, reps_val in [(10, Decimal('90.0'), Decimal('6')), (6, Decimal('95.0'), Decimal('6')), (2, Decimal('100.0'), Decimal('5'))]:
                log_dt = timezone.now() - datetime.timedelta(days=day_offset, hours=3)
                WorkoutLog.objects.create(
                    user=demo_user,
                    routine=routine,
                    exercise=squat_ex,
                    weight=weight_val,
                    repetitions=reps_val,
                    date=log_dt,
                )
            self.stdout.write('  [Logs] Created 7 recent workout session logs for Bench Press & Squats')

        # 8. Add Body Weight Tracking History (Past 30 Days)
        cat_weight = Category.get_or_create_body_weight(demo_user, unit=demo_user.userprofile.weight_unit)
        if not Measurement.objects.filter(category=cat_weight).exists():
            weight_progression = [
                (28, Decimal('78.5')),
                (21, Decimal('78.1')),
                (14, Decimal('77.6')),
                (7, Decimal('77.2')),
                (2, Decimal('76.8')),
            ]
            for days_ago, val in weight_progression:
                m_date = timezone.now() - datetime.timedelta(days=days_ago)
                Measurement.objects.create(
                    category=cat_weight,
                    value=val,
                    date=m_date,
                )
            self.stdout.write('  [Weight] Populated 30-day downward weight trend (78.5 kg -> 76.8 kg)')

        # 9. Add Sample Nutrition Plan for demo user
        if not NutritionPlan.objects.filter(user=demo_user).exists():
            plan = NutritionPlan.objects.create(
                user=demo_user,
                description='High-Protein Clean Hypertrophy Plan (2,700 kcal)',
                start=today - datetime.timedelta(days=20),
            )
            # Meal 1: Breakfast
            m1 = Meal.objects.create(plan=plan, order=1, time=datetime.time(8, 0))
            MealItem.objects.create(meal=m1, ingredient=ing_map['Rolled Whole Oats'], amount=Decimal('80.0'), order=1)
            MealItem.objects.create(meal=m1, ingredient=ing_map['Whole Large Eggs'], amount=Decimal('150.0'), order=2)
            MealItem.objects.create(meal=m1, ingredient=ing_map['Fresh Banana'], amount=Decimal('120.0'), order=3)

            # Meal 2: Post-Workout Lunch
            m2 = Meal.objects.create(plan=plan, order=2, time=datetime.time(12, 30))
            MealItem.objects.create(meal=m2, ingredient=ing_map['Chicken Breast (Grilled)'], amount=Decimal('200.0'), order=1)
            MealItem.objects.create(meal=m2, ingredient=ing_map['Cooked Brown Rice'], amount=Decimal('200.0'), order=2)
            MealItem.objects.create(meal=m2, ingredient=ing_map['Steamed Fresh Broccoli'], amount=Decimal('100.0'), order=3)

            # Meal 3: Afternoon Snack
            m3 = Meal.objects.create(plan=plan, order=3, time=datetime.time(16, 0))
            MealItem.objects.create(meal=m3, ingredient=ing_map['Greek Yogurt (0% Plain)'], amount=Decimal('250.0'), order=1)
            MealItem.objects.create(meal=m3, ingredient=ing_map['Whey Protein Isolate'], amount=Decimal('30.0'), order=2)
            MealItem.objects.create(meal=m3, ingredient=ing_map['Natural Peanut Butter'], amount=Decimal('25.0'), order=3)

            # Meal 4: Dinner
            m4 = Meal.objects.create(plan=plan, order=4, time=datetime.time(19, 30))
            MealItem.objects.create(meal=m4, ingredient=ing_map['Atlantic Salmon Fillet'], amount=Decimal('180.0'), order=1)
            MealItem.objects.create(meal=m4, ingredient=ing_map['Baked Sweet Potato'], amount=Decimal('200.0'), order=2)
            MealItem.objects.create(meal=m4, ingredient=ing_map['Extra Virgin Olive Oil'], amount=Decimal('10.0'), order=3)

            self.stdout.write('  [Nutrition] Created 4-meal High Protein Nutrition Plan')

        self.stdout.write(self.style.SUCCESS('Successfully populated mock data for HEALTHYFY TRACKER!'))
