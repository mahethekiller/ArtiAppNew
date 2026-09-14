import os

migration_content = r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // 1. Enrich arti_deities table with sacred metadata
        Schema::table('arti_deities', function (Blueprint $table) {
            if (!Schema::hasColumn('arti_deities', 'slug')) {
                $table->string('slug')->nullable()->unique()->after('id');
            }
            if (!Schema::hasColumn('arti_deities', 'name_devanagari')) {
                $table->string('name_devanagari')->nullable()->after('name');
            }
            if (!Schema::hasColumn('arti_deities', 'title_sub')) {
                $table->string('title_sub')->nullable()->after('name_devanagari');
            }
            if (!Schema::hasColumn('arti_deities', 'day_of_week')) {
                $table->string('day_of_week')->nullable()->after('title_sub');
            }
            if (!Schema::hasColumn('arti_deities', 'day_hindi')) {
                $table->string('day_hindi')->nullable()->after('day_of_week');
            }
            if (!Schema::hasColumn('arti_deities', 'theme_color')) {
                $table->string('theme_color')->nullable()->after('day_hindi');
            }
            if (!Schema::hasColumn('arti_deities', 'accent_color')) {
                $table->string('accent_color')->nullable()->after('theme_color');
            }
            if (!Schema::hasColumn('arti_deities', 'icon')) {
                $table->string('icon')->nullable()->after('accent_color');
            }
            $table->string('description')->nullable()->change();
            $table->string('image_url')->nullable()->change();
        });

        // 2. Enrich arti_aartis table with comprehensive fields
        Schema::table('arti_aartis', function (Blueprint $table) {
            if (!Schema::hasColumn('arti_aartis', 'slug')) {
                $table->string('slug')->nullable()->unique()->after('id');
            }
            if (!Schema::hasColumn('arti_aartis', 'title_devanagari')) {
                $table->string('title_devanagari')->nullable()->after('title');
            }
            if (!Schema::hasColumn('arti_aartis', 'deity_name')) {
                $table->string('deity_name')->nullable()->after('deity_id');
            }
            if (!Schema::hasColumn('arti_aartis', 'deity_devanagari')) {
                $table->string('deity_devanagari')->nullable()->after('deity_name');
            }
            if (!Schema::hasColumn('arti_aartis', 'image_url')) {
                $table->string('image_url')->nullable()->after('category');
            }
            if (!Schema::hasColumn('arti_aartis', 'timing')) {
                $table->string('timing')->nullable()->after('duration');
            }
            if (!Schema::hasColumn('arti_aartis', 'timing_devanagari')) {
                $table->string('timing_devanagari')->nullable()->after('timing');
            }
            if (!Schema::hasColumn('arti_aartis', 'duration_minutes')) {
                $table->integer('duration_minutes')->nullable()->after('timing_devanagari');
            }
            if (!Schema::hasColumn('arti_aartis', 'significance')) {
                $table->text('significance')->nullable()->after('duration_minutes');
            }
            if (!Schema::hasColumn('arti_aartis', 'significance_devanagari')) {
                $table->text('significance_devanagari')->nullable()->after('significance');
            }
            if (!Schema::hasColumn('arti_aartis', 'meaning_short')) {
                $table->text('meaning_short')->nullable()->after('significance_devanagari');
            }
            if (!Schema::hasColumn('arti_aartis', 'lyrics_json')) {
                $table->json('lyrics_json')->nullable()->after('lyrics');
            }
            if (!Schema::hasColumn('arti_aartis', 'lyrics_transliteration')) {
                $table->json('lyrics_transliteration')->nullable()->after('lyrics_json');
            }
            if (!Schema::hasColumn('arti_aartis', 'is_popular')) {
                $table->boolean('is_popular')->default(false)->after('lyrics_transliteration');
            }

            $table->string('subtitle')->nullable()->change();
            $table->string('category')->nullable()->change();
            $table->string('duration')->nullable()->change();
            $table->string('audio_url')->nullable()->change();
            $table->string('video_url')->nullable()->change();
            $table->text('lyrics')->nullable()->change();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('arti_deities', function (Blueprint $table) {
            $table->dropColumn([
                'slug',
                'name_devanagari',
                'title_sub',
                'day_of_week',
                'day_hindi',
                'theme_color',
                'accent_color',
                'icon'
            ]);
        });

        Schema::table('arti_aartis', function (Blueprint $table) {
            $table->dropColumn([
                'slug',
                'title_devanagari',
                'deity_name',
                'deity_devanagari',
                'image_url',
                'timing',
                'timing_devanagari',
                'duration_minutes',
                'significance',
                'significance_devanagari',
                'meaning_short',
                'lyrics_json',
                'lyrics_transliteration',
                'is_popular'
            ]);
        });
    }
};
'''

dest = r"D:\SOFTWARES\xampp82new\htdocs\toolsite\database\migrations\2026_09_14_180000_update_arti_tables_for_sacred_aarti_collection.php"
with open(dest, "w", encoding="utf-8") as f:
    f.write(migration_content.strip())

print("Migration written successfully.")
