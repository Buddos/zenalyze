from django.db import migrations


LEGACY_MEDITATION_MEDIA = {
    'Mindfulness Body Scan Meditation': (
        'exercise_6a09f6bd75a97.mp4',
        'thumb_6a0a028907a52.webp',
    ),
    'Loving-Kindness (Metta) Meditation': (
        'exercise_6a0a02d9c47f0.mp4',
        'thumb_6a0a028907a52.webp',
    ),
}

SEEDED_BREATHING_MEDIA = {
    'Box Breathing for Instant Calm': (
        'exercise_6a09f6bd75a97.mp4',
        'thumb_6a0a01df4eefb.jpeg',
    ),
    '4-7-8 Relaxing Breath Technique': (
        'exercise_6a0a02d9c47f0.mp4',
        'thumb_6a0a02d9c4a0c.jpeg',
    ),
}


def remove_misassigned_breathing_media(apps, schema_editor):
    Exercise = apps.get_model('wellness', 'Exercise')
    MediaAsset = apps.get_model('community', 'MediaAsset')

    for title, (video_name, thumbnail_name) in LEGACY_MEDITATION_MEDIA.items():
        exercise = Exercise.objects.filter(title=title).first()
        if not exercise:
            continue

        updated_fields = []
        if exercise.video_file and exercise.video_file.name.rsplit('/', 1)[-1] == video_name:
            exercise.video_file = ''
            updated_fields.append('video_file')
        if exercise.thumbnail_file and exercise.thumbnail_file.name.rsplit('/', 1)[-1] == thumbnail_name:
            exercise.thumbnail_file = ''
            updated_fields.append('thumbnail_file')
        if exercise.thumbnail_image and exercise.thumbnail_image.rsplit('/', 1)[-1] == thumbnail_name:
            exercise.thumbnail_image = ''
            updated_fields.append('thumbnail_image')
        if exercise.media_asset_id:
            asset = MediaAsset.objects.filter(pk=exercise.media_asset_id).only('file').first()
            if asset and asset.file.name.rsplit('/', 1)[-1] == video_name:
                exercise.media_asset_id = None
                updated_fields.append('media_asset')

        if updated_fields:
            exercise.save(update_fields=updated_fields)

    for title, (video_name, thumbnail_name) in SEEDED_BREATHING_MEDIA.items():
        exercise = Exercise.objects.filter(title=title).first()
        if not exercise:
            continue

        updated_fields = []
        video_matches = bool(exercise.video_file) and exercise.video_file.name.rsplit('/', 1)[-1] == video_name
        if exercise.media_asset_id and not video_matches:
            asset = MediaAsset.objects.filter(pk=exercise.media_asset_id).only('file').first()
            video_matches = bool(asset) and asset.file.name.rsplit('/', 1)[-1] == video_name
        if video_matches:
            exercise.video_url = f'/static/uploads/exercises/videos/{video_name}'
            exercise.video_type = 'file'
            updated_fields.extend(['video_url', 'video_type'])

        thumbnail_matches = bool(exercise.thumbnail_file) and exercise.thumbnail_file.name.rsplit('/', 1)[-1] == thumbnail_name
        if exercise.media_asset_id and not thumbnail_matches:
            asset = MediaAsset.objects.filter(pk=exercise.media_asset_id).only('thumbnail').first()
            thumbnail_matches = bool(asset and asset.thumbnail) and asset.thumbnail.name.rsplit('/', 1)[-1] == thumbnail_name
        if thumbnail_matches:
            exercise.thumbnail_image = f'/static/uploads/exercises/thumbnails/{thumbnail_name}'
            updated_fields.append('thumbnail_image')

        if updated_fields:
            exercise.save(update_fields=updated_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0006_alter_exercise_category'),
    ]

    operations = [
        migrations.RunPython(remove_misassigned_breathing_media, migrations.RunPython.noop),
    ]
