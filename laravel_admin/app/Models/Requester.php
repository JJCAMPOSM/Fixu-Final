<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Requester extends Model
{
    protected $table = 'requesters';

    protected $fillable = [
        'name',
        'email',
        'phone',
    ];
}
