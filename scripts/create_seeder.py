import os

seeder_code = r'''<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Arti\Deity;
use App\Models\Arti\Aarti;
use Illuminate\Support\Facades\File;

class ArtiDatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $categoriesPath = 'd:/SOFTWARES/xampp82new/htdocs/androidapps/arti/src/assets/data/categories.json';
        $artiesPath = 'd:/SOFTWARES/xampp82new/htdocs/androidapps/arti/src/assets/data/arties.json';

        if (!File::exists($categoriesPath) || !File::exists($artiesPath)) {
            $this->command->error('Data JSON files not found!');
            return;
        }

        $categories = json_decode(File::get($categoriesPath), true);
        $arties = json_decode(File::get($artiesPath), true);

        // 1. Purge all dummy aartis that do not start with 'arti-'
        $deletedDummies = Aarti::where('slug', 'not like', 'arti-%')->delete();
        $this->command->info("Purged {$deletedDummies} dummy/mock aartis from MySQL.");

        // 2. Purge unused deities
        $validSlugs = array_column($categories, 'id');
        Deity::whereNotIn('slug', $validSlugs)->delete();

        $this->command->info('Seeding Deities...');
        $deityMap = [];

        foreach ($categories as $cat) {
            $deity = Deity::updateOrCreate(
                ['slug' => $cat['id']],
                [
                    'name' => $cat['name'],
                    'name_devanagari' => $cat['name_devanagari'] ?? null,
                    'title_sub' => $cat['title_sub'] ?? null,
                    'day_of_week' => $cat['day_of_week'] ?? null,
                    'day_hindi' => $cat['day_hindi'] ?? null,
                    'theme_color' => $cat['theme_color'] ?? '#E65100',
                    'accent_color' => $cat['accent_color'] ?? '#FFA726',
                    'icon' => $cat['icon'] ?? '🕉️',
                    'description' => $cat['title_sub'] ?? ($cat['name'] . ' Aarti Collection'),
                    'image_url' => '/images/arties/arti-' . $cat['id'] . '-aarti.jpg'
                ]
            );
            $deityMap[$cat['id']] = $deity->id;
        }

        $this->command->info('Seeding ' . count($arties) . ' Authentic Aartis...');

        foreach ($arties as $a) {
            $catId = $a['category_id'] ?? 'special';
            $deityId = $deityMap[$catId] ?? ($deityMap['special'] ?? 1);

            // Plain text version of lyrics for backward compatibility
            $plainLyrics = '';
            if (!empty($a['lyrics_devanagari']) && is_array($a['lyrics_devanagari'])) {
                foreach ($a['lyrics_devanagari'] as $sec) {
                    if (!empty($sec['lines'])) {
                        $plainLyrics .= implode("\n", $sec['lines']) . "\n\n";
                    }
                }
            }

            // Local image path in Laravel public storage
            $imageUrl = null;
            if (!empty($a['image'])) {
                $filename = basename($a['image']);
                $imageUrl = '/images/arties/' . $filename;
            }

            Aarti::updateOrCreate(
                ['slug' => $a['id']],
                [
                    'deity_id' => $deityId,
                    'deity_name' => $a['deity'] ?? '',
                    'deity_devanagari' => $a['deity_devanagari'] ?? '',
                    'title' => $a['title'] ?? '',
                    'title_devanagari' => $a['title_devanagari'] ?? '',
                    'subtitle' => ($a['deity'] ?? '') . ' • ' . ($a['timing'] ?? 'Daily Aarti'),
                    'category' => $catId,
                    'image_url' => $imageUrl,
                    'duration' => !empty($a['duration_minutes']) ? ($a['duration_minutes'] . ' min') : '3 min',
                    'duration_minutes' => $a['duration_minutes'] ?? 3,
                    'timing' => $a['timing'] ?? 'Daily Pooja / Aarti',
                    'timing_devanagari' => $a['timing_devanagari'] ?? 'नित्य पूजन एवं आरती',
                    'significance' => $a['significance'] ?? '',
                    'significance_devanagari' => $a['significance_devanagari'] ?? '',
                    'meaning_short' => $a['meaning_short'] ?? '',
                    'audio_url' => null,
                    'video_url' => null,
                    'lyrics' => trim($plainLyrics),
                    'lyrics_json' => $a['lyrics_devanagari'] ?? [],
                    'lyrics_transliteration' => $a['lyrics_transliteration'] ?? [],
                    'is_popular' => !empty($a['popular']),
                ]
            );
        }

        $this->command->info('Seeded ' . Deity::count() . ' deities and ' . Aarti::count() . ' aartis successfully into MySQL!');
    }
}
'''

path = r"D:\SOFTWARES\xampp82new\htdocs\toolsite\database\seeders\ArtiDatabaseSeeder.php"
with open(path, "w", encoding="utf-8") as f:
    f.write(seeder_code.strip())

print("Created ArtiDatabaseSeeder.php successfully with dummy purge.")
