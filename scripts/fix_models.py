import os

aarti_model = r'''<?php

namespace App\Models\Arti;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Aarti extends Model
{
    protected $table = 'arti_aartis';

    protected $fillable = [
        'slug',
        'deity_id',
        'deity_name',
        'deity_devanagari',
        'title',
        'title_devanagari',
        'subtitle',
        'category',
        'image_url',
        'duration',
        'duration_minutes',
        'timing',
        'timing_devanagari',
        'significance',
        'significance_devanagari',
        'meaning_short',
        'audio_url',
        'video_url',
        'lyrics',
        'lyrics_json',
        'lyrics_transliteration',
        'is_popular',
    ];

    protected $casts = [
        'lyrics_json' => 'array',
        'lyrics_transliteration' => 'array',
        'is_popular' => 'boolean',
        'duration_minutes' => 'integer',
    ];

    public function deity(): BelongsTo
    {
        return $this->belongsTo(Deity::class, 'deity_id');
    }

    public function getImageUrlAttribute(?string $value): ?string
    {
        if ($value && !str_starts_with($value, 'http')) {
            return url($value);
        }
        return $value;
    }
}
'''

deity_model = r'''<?php

namespace App\Models\Arti;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Deity extends Model
{
    protected $table = 'arti_deities';

    protected $fillable = [
        'slug',
        'name',
        'name_devanagari',
        'title_sub',
        'day_of_week',
        'day_hindi',
        'theme_color',
        'accent_color',
        'icon',
        'description',
        'image_url'
    ];

    public function aartis(): HasMany
    {
        return $this->hasMany(Aarti::class, 'deity_id');
    }

    public function galleryImages(): HasMany
    {
        return $this->hasMany(GalleryImage::class, 'deity_id');
    }

    public function getImageUrlAttribute(?string $value): ?string
    {
        if ($value && !str_starts_with($value, 'http')) {
            return url($value);
        }
        return $value;
    }
}
'''

with open(r"D:\SOFTWARES\xampp82new\htdocs\toolsite\app\Models\Arti\Aarti.php", "w", encoding="utf-8") as f:
    f.write(aarti_model.strip())

with open(r"D:\SOFTWARES\xampp82new\htdocs\toolsite\app\Models\Arti\Deity.php", "w", encoding="utf-8") as f:
    f.write(deity_model.strip())

print("Cleanly wrote Aarti and Deity models.")
