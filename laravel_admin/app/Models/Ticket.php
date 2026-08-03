<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Ticket extends Model
{
    protected $table = 'tickets';

    protected $fillable = [
        'title',
        'body',
        'requester_id',
        'category_id',
        'team_id',
        'assignee_team_member_id',
        'status',
        'priority',
        'building',
        'classroom',
        'equipment_type',
    ];

    public function requester()
    {
        return $this->belongsTo(Requester::class, 'requester_id');
    }

    public function category()
    {
        return $this->belongsTo(Category::class, 'category_id');
    }

    public function team()
    {
        return $this->belongsTo(Team::class, 'team_id');
    }

    public function assignee()
    {
        return $this->belongsTo(TeamMember::class, 'assignee_team_member_id');
    }
}
